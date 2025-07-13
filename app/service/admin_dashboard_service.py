from app.models.admin_dashboard import AdminDashboard
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

class AdminDashboardService:
    def __init__(self):
        self.model = AdminDashboard()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get all admin dashboard statistics in a single call"""
        return {
            'total_employees': self.model.get_total_active_employees(),
            'pending_requests': self.model.get_pending_attendance_requests(),
            'approved_requests': self.model.get_approved_attendance_requests(),
            'employees_on_leave': self.model.get_employees_on_leave_today()
        }
    
    # def get_weekly_attendance_for_chart(self, department: str = None) -> List[Dict[str, any]]:
    #     """
    #     Get weekly attendance data for charts
    #     Args:
    #         department: Optional department filter
    #     Returns:
    #         Formatted data for frontend charts
    #     """
    #     try:
    #         # data = self.model.get_weekly_attendance_for_chart(department)
    #         data = self.model.get_present_employees_this_week()
    #         print(f"**********************{data}")
    #         # Calculate attendance rates
    #         for day in data:
    #             total = day['present'] + day['absent']
    #             day['attendance_rate'] = round(
    #                 (day['present'] / total * 100), 2
    #             ) if total > 0 else 0.0
            
    #         return data
            
    #     except Exception as e:
    #         print(f"Error getting weekly attendance: {str(e)}")
    #         return self._get_empty_week_template()



    def get_weekly_attendance_for_chart(self, department: str = None) -> List[Dict[str, Any]]:
        try:
            raw_data = self.model.get_present_employees_this_week()

            # Initialize summary dict with day names as keys and counts for present/absent
            week_summary = defaultdict(lambda: {'present': 0, 'absent': 0, 'date': ''})

            for record in raw_data:
                date_str = record['date']  # e.g., '2025-07-07'
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                day_name = date_obj.strftime('%a')  # 'Mon', 'Tue', etc.

                # Use full day name or abbreviated consistently (here abbreviated)
                # Count present if approval_status is 'Approved', else absent
                if record.get('approval_status') == 'Approved':
                    week_summary[day_name]['present'] += 1
                else:
                    week_summary[day_name]['absent'] += 1

                # Store the date string (last occurrence will be stored, which is fine)
                week_summary[day_name]['date'] = date_str

            # Ensure all days of the week are present in summary (Mon-Sun)
            all_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            data = []
            for day in all_days:
                counts = week_summary.get(day, {'present': 0, 'absent': 0, 'date': ''})
                total = counts['present'] + counts['absent']
                attendance_rate = round((counts['present'] / total) * 100, 2) if total > 0 else 0.0
                data.append({
                    'name': day,
                    'present': counts['present'],
                    'absent': counts['absent'],
                    'attendance_rate': attendance_rate,
                    'date': counts['date']
                })

            return data

        except Exception as e:
            print(f"Error getting weekly attendance: {str(e)}")
            return self._get_empty_week_template()


    def _get_empty_week_template(self) -> List[Dict[str, any]]:
        """Return empty week template"""
        return [
            {'name': 'Mon', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Tue', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Wed', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Thu', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Fri', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Sat', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Sun', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''}
        ]
    
    
    def get_employee_growth_data(self, limit: int = 12) -> List[Dict[str, any]]:
        """
        Get monthly employee growth data for visualization
        Args:
            limit: Number of months to return (default 12)
        Returns:
            List of dictionaries with:
            - month: Month name (e.g., 'Jan')
            - employees: Cumulative employee count
        """
        try:
            raw_data = self.model.get_employee_growth_data()
            
            if not raw_data:
                return []

            # Process into monthly cumulative counts
            monthly_counts = {}
            cumulative_count = 0
            
            for record in raw_data:
                date = datetime.strptime(record['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')  # Group by month
                
                if month_key not in monthly_counts:
                    monthly_counts[month_key] = {
                        'count': 0,
                        'label': date.strftime('%b')  # Jan, Feb, etc.
                    }
                monthly_counts[month_key]['count'] += 1
            
            # Convert to sorted list with cumulative counts
            sorted_months = sorted(monthly_counts.items(), key=lambda x: x[0])
            
            processed_data = []
            for month_key, data in sorted_months[-limit:]:
                cumulative_count += data['count']
                processed_data.append({
                    'month': data['label'],
                    'employees': cumulative_count
                })
            
            return processed_data

        except Exception as e:
            print(f"Error getting employee growth data: {str(e)}")
            return []

    def _get_empty_week_template(self) -> List[Dict[str, any]]:
        """Return empty week template"""
        return [
            {'name': 'Mon', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Tue', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Wed', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Thu', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Fri', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Sat', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''},
            {'name': 'Sun', 'present': 0, 'absent': 0, 'attendance_rate': 0.0, 'date': ''}
        ]
    
    def get_employee_counts_by_department(self) -> Dict[str, int]:
        """
        Get employee counts by department
        Returns:
            Dictionary with department names and employee counts
            Example: {'HR': 5, 'IT': 12, 'Finance': 8}
        """
        try:
            return self.model.get_employee_counts_by_department()
        except Exception as e:
            print(f"Error getting department counts: {str(e)}")
            return {}  # Return empty dict on error