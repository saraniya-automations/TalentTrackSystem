from app.models.admin_dashboard import AdminDashboard
from typing import Dict, Any, List
from datetime import datetime

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
    
    def get_weekly_attendance_for_chart(self, department: str = None) -> List[Dict[str, any]]:
        """
        Get weekly attendance data for charts
        Args:
            department: Optional department filter
        Returns:
            Formatted data for frontend charts
        """
        try:
            data = self.model.get_weekly_attendance_for_chart(department)
            
            # Calculate attendance rates
            for day in data:
                total = day['present'] + day['absent']
                day['attendance_rate'] = round(
                    (day['present'] / total * 100), 2
                ) if total > 0 else 0.0
            
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
    
    # def get_employee_growth_data(self, timeframe: str = 'monthly', limit: int = 12) -> List[Dict[str, any]]:
    #     """
    #     Get employee growth data for visualization
    #     Args:
    #         timeframe: 'monthly' or 'quarterly'
    #         limit: number of periods to return (default 12)
    #     Returns:
    #         List of dictionaries with:
    #         - month: Month name (e.g., 'Jan') or quarter (e.g., 'Q1 23')
    #         - employees: Cumulative employee count
    #     """
    #     try:
    #         raw_data = self.model.get_employee_growth_raw_data()
            
    #         if not raw_data:
    #             return []

    #         # Process raw data into requested timeframe
    #         processed_data = self._process_growth_data(
    #             raw_data, 
    #             timeframe=timeframe,
    #             limit=limit
    #         )

    #         return processed_data

    #     except Exception as e:
    #         print(f"Error getting employee growth data: {str(e)}")
    #         return []    

    # def _process_growth_data(self, raw_data: List[Dict], timeframe: str, limit: int) -> List[Dict]:
        """Process raw employee growth data into requested timeframe format"""
        processed = []
        current_period = None
        period_count = 0
        
        for record in raw_data:
            date = datetime.strptime(record['date'], '%Y-%m-%d')
            
            if timeframe == 'monthly':
                period_key = date.strftime('%Y-%m')
                period_label = date.strftime('%b')  # Jan, Feb, etc.
            # else:  # quarterly
            #     quarter = (date.month - 1) // 3 + 1
            #     period_key = f"{date.year}-Q{quarter}"
            #     period_label = f"Q{quarter} {date.strftime('%y')}"  # Q1 23, etc.
            
            if period_key != current_period:
                if current_period is not None:
                    processed.append({
                        'month': current_label,
                        'employees': current_count
                    })
                    period_count += 1
                    if period_count >= limit:
                        break
                
                current_period = period_key
                current_label = period_label
                current_count = 0
            
            current_count += 1
        
        # Add the last period if we haven't reached the limit
        if current_period is not None and period_count < limit:
            processed.append({
                'month': current_label,
                'employees': current_count
            })
        
        return processed
    
    # def get_employee_growth_data(self, limit: int = 12) -> List[Dict[str, any]]:
    #     """
    #     Get monthly employee growth data (Service Layer)
    #     Args:
    #         limit: Number of months to return (default 12)
    #     Returns:
    #         List of {'month': 'Jan', 'employees': 20}
    #     """
    #     try:
    #         # Get raw data from Model Layer
    #         raw_counts = self.model.get_monthly_employee_counts()
            
    #         if not raw_counts:
    #             return []

    #         # Process into frontend format
    #         return self._format_growth_data(raw_counts, limit)
            
    #     except Exception as e:
    #         print(f"Error processing growth data: {str(e)}")
    #         return []
        
    # def _format_growth_data(self, monthly_counts: Dict[str, int], limit: int) -> List[Dict]:
    #     """Convert raw counts to frontend format"""
    #     # Sort months chronologically
    #     sorted_months = sorted(
    #         monthly_counts.items(),
    #         key=lambda x: datetime.strptime(x[0], '%Y-%m')
    #     )
        
    #     # Build cumulative counts
    #     cumulative = 0
    #     result = []
    #     for month_key, count in sorted_months[-limit:]:
    #         cumulative += count
    #         result.append({
    #             'month': datetime.strptime(month_key, '%Y-%m').strftime('%b'),
    #             'employees': cumulative
    #         })
        
    #     return result

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