import sqlite3
import pandas as pd
from datetime import datetime

def create_excel_from_database(db_path, excel_path):
    """Create Excel file with data from all tables in the database"""
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    # Create Excel writer
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        
        # Get all table names
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            print(f"Processing table: {table}")
            
            # Read table data into DataFrame
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            
            # Write to Excel sheet
            df.to_excel(writer, sheet_name=table, index=False)
            
            # Get worksheet to adjust column widths
            worksheet = writer.sheets[table]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Create summary sheet
        summary_data = []
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            column_info = [f"{col[1]} ({col[2]})" for col in columns]
            
            summary_data.append({
                'Table': table,
                'Row Count': count,
                'Columns': ', '.join(column_info)
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Adjust summary sheet column widths
        summary_ws = writer.sheets['Summary']
        for column in summary_ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 80)
            summary_ws.column_dimensions[column_letter].width = adjusted_width
    
    conn.close()
    print(f"Excel file created successfully: {excel_path}")

if __name__ == "__main__":
    db_path = "quranenc_main.db"
    excel_path = f"quranenc_database_mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    create_excel_from_database(db_path, excel_path)