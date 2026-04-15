"""Google Sheets integration for analytics."""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


class GoogleSheetsIntegration:
    """Google Sheets integration for order analytics."""
    
    def __init__(self, credentials_file: str, spreadsheet_id: str):
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self._client = None
        self._spreadsheet = None
    
    def _get_client(self) -> gspread.Client:
        """Get authenticated Google Sheets client."""
        if self._client is None:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials
            if os.path.exists(self.credentials_file):
                creds = Credentials.from_service_account_file(
                    self.credentials_file, 
                    scopes=scope
                )
            else:
                # Try to load from environment variable
                creds_json = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
                if creds_json:
                    creds_info = json.loads(creds_json)
                    creds = Credentials.from_service_account_info(
                        creds_info, 
                        scopes=scope
                    )
                else:
                    raise ValueError("Google Sheets credentials not found")
            
            self._client = gspread.authorize(creds)
        
        return self._client
    
    def _get_spreadsheet(self) -> gspread.Spreadsheet:
        """Get spreadsheet instance."""
        if self._spreadsheet is None:
            client = self._get_client()
            self._spreadsheet = client.open_by_key(self.spreadsheet_id)
        
        return self._spreadsheet
    
    async def log_order(self, order_data: Dict[str, Any]) -> bool:
        """Log order to Google Sheets."""
        try:
            spreadsheet = self._get_spreadsheet()
            
            # Get or create "Orders" worksheet
            try:
                worksheet = spreadsheet.worksheet("Orders")
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet("Orders", rows=1000, cols=20)
                # Add headers
                headers = [
                    "Order ID", "User ID", "User Name", "User Phone", "Telegram ID",
                    "Order Type", "Payment Method", "Status", "Total Amount", "Items Count",
                    "Delivery Address", "Delivery Phone", "Comment", "Created At", "Updated At"
                ]
                worksheet.append_row(headers)
            
            # Prepare order data
            row_data = [
                order_data.get("order_id", ""),
                order_data.get("user_id", ""),
                order_data.get("user_name", ""),
                order_data.get("user_phone", ""),
                order_data.get("user_telegram_id", ""),
                order_data.get("order_type", ""),
                order_data.get("payment_method", ""),
                order_data.get("status", ""),
                order_data.get("total_amount", 0),
                order_data.get("items_count", 0),
                order_data.get("delivery_address", ""),
                order_data.get("delivery_phone", ""),
                order_data.get("comment", ""),
                order_data.get("created_at", ""),
                order_data.get("updated_at", "")
            ]
            
            # Add row to worksheet
            worksheet.append_row(row_data)
            
            print(f"✅ Order {order_data.get('order_id')} logged to Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Failed to log order to Google Sheets: {e}")
            return False
    
    async def log_order_status_change(self, order_id: str, old_status: str, new_status: str, timestamp: str) -> bool:
        """Log order status change to Google Sheets."""
        try:
            spreadsheet = self._get_spreadsheet()
            
            # Get or create "Status Changes" worksheet
            try:
                worksheet = spreadsheet.worksheet("Status Changes")
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet("Status Changes", rows=1000, cols=10)
                # Add headers
                headers = ["Order ID", "Old Status", "New Status", "Timestamp"]
                worksheet.append_row(headers)
            
            # Add status change record
            row_data = [order_id, old_status, new_status, timestamp]
            worksheet.append_row(row_data)
            
            print(f"✅ Status change for order {order_id} logged to Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Failed to log status change to Google Sheets: {e}")
            return False
    
    async def update_daily_summary(self, date: str, summary_data: Dict[str, Any]) -> bool:
        """Update daily summary in Google Sheets."""
        try:
            spreadsheet = self._get_spreadsheet()
            
            # Get or create "Daily Summary" worksheet
            try:
                worksheet = spreadsheet.worksheet("Daily Summary")
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet("Daily Summary", rows=1000, cols=10)
                # Add headers
                headers = [
                    "Date", "Total Orders", "Total Revenue", "Average Order Value",
                    "Delivery Orders", "Pickup Orders", "Online Payments", "Cash Payments",
                    "New Users", "Active Users"
                ]
                worksheet.append_row(headers)
            
            # Check if date already exists
            try:
                cell = worksheet.find(date)
                if cell:
                    # Update existing row
                    row_num = cell.row
                    row_data = [
                        date,
                        summary_data.get("total_orders", 0),
                        summary_data.get("total_revenue", 0),
                        summary_data.get("average_order_value", 0),
                        summary_data.get("delivery_orders", 0),
                        summary_data.get("pickup_orders", 0),
                        summary_data.get("online_payments", 0),
                        summary_data.get("cash_payments", 0),
                        summary_data.get("new_users", 0),
                        summary_data.get("active_users", 0)
                    ]
                    
                    # Update row
                    for i, value in enumerate(row_data, 1):
                        worksheet.update_cell(row_num, i, value)
                else:
                    # Add new row
                    row_data = [
                        date,
                        summary_data.get("total_orders", 0),
                        summary_data.get("total_revenue", 0),
                        summary_data.get("average_order_value", 0),
                        summary_data.get("delivery_orders", 0),
                        summary_data.get("pickup_orders", 0),
                        summary_data.get("online_payments", 0),
                        summary_data.get("cash_payments", 0),
                        summary_data.get("new_users", 0),
                        summary_data.get("active_users", 0)
                    ]
                    worksheet.append_row(row_data)
            except gspread.CellNotFound:
                # Add new row
                row_data = [
                    date,
                    summary_data.get("total_orders", 0),
                    summary_data.get("total_revenue", 0),
                    summary_data.get("average_order_value", 0),
                    summary_data.get("delivery_orders", 0),
                    summary_data.get("pickup_orders", 0),
                    summary_data.get("online_payments", 0),
                    summary_data.get("cash_payments", 0),
                    summary_data.get("new_users", 0),
                    summary_data.get("active_users", 0)
                ]
                worksheet.append_row(row_data)
            
            print(f"✅ Daily summary for {date} updated in Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update daily summary in Google Sheets: {e}")
            return False
    
    async def get_orders_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get orders data from Google Sheets."""
        try:
            spreadsheet = self._get_spreadsheet()
            
            try:
                worksheet = spreadsheet.worksheet("Orders")
            except gspread.WorksheetNotFound:
                return []
            
            # Get all records
            records = worksheet.get_all_records()
            
            # Filter by date if specified
            if start_date or end_date:
                filtered_records = []
                for record in records:
                    created_at = record.get("Created At", "")
                    if start_date and created_at < start_date:
                        continue
                    if end_date and created_at > end_date:
                        continue
                    filtered_records.append(record)
                return filtered_records
            
            return records
            
        except Exception as e:
            print(f"❌ Failed to get orders data from Google Sheets: {e}")
            return []
    
    async def get_daily_summary(self, date: str) -> Optional[Dict[str, Any]]:
        """Get daily summary from Google Sheets."""
        try:
            spreadsheet = self._get_spreadsheet()
            
            try:
                worksheet = spreadsheet.worksheet("Daily Summary")
            except gspread.WorksheetNotFound:
                return None
            
            # Find row with specified date
            try:
                cell = worksheet.find(date)
                if cell:
                    row_num = cell.row
                    row_data = worksheet.row_values(row_num)
                    
                    if len(row_data) >= 10:
                        return {
                            "date": row_data[0],
                            "total_orders": int(row_data[1]) if row_data[1] else 0,
                            "total_revenue": int(row_data[2]) if row_data[2] else 0,
                            "average_order_value": int(row_data[3]) if row_data[3] else 0,
                            "delivery_orders": int(row_data[4]) if row_data[4] else 0,
                            "pickup_orders": int(row_data[5]) if row_data[5] else 0,
                            "online_payments": int(row_data[6]) if row_data[6] else 0,
                            "cash_payments": int(row_data[7]) if row_data[7] else 0,
                            "new_users": int(row_data[8]) if row_data[8] else 0,
                            "active_users": int(row_data[9]) if row_data[9] else 0
                        }
            except gspread.CellNotFound:
                pass
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to get daily summary from Google Sheets: {e}")
            return None
