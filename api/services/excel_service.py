import pandas as pd
import os
from datetime import datetime

def generate_movements_excel(movimientos_data, output_path):
    """
    Generate Excel report for movements.

    Args:
        movimientos_data: List of movement dictionaries with joined data
        output_path: Path where to save the Excel file

    Returns:
        Boolean indicating success
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create DataFrame
        df = pd.DataFrame(movimientos_data)

        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Write data
            df.to_excel(writer, sheet_name='Movimientos', index=False)

            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Movimientos']

            # Format header row
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)
                cell.fill = cell.fill.copy(fgColor="DBEAFE")

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
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            # Freeze top row
            worksheet.freeze_panes = 'A2'

        return True

    except Exception as e:
        print(f"Error generating Excel report: {e}")
        return False

def generate_deliveries_excel(manifiestos_data, output_path):
    """
    Generate Excel report for deliveries (manifests).

    Args:
        manifiestos_data: List of manifest dictionaries with details
        output_path: Path where to save the Excel file

    Returns:
        Boolean indicating success
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create DataFrame
        df = pd.DataFrame(manifiestos_data)

        # Create Excel writer
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Write data
            df.to_excel(writer, sheet_name='Entregas', index=False)

            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Entregas']

            # Format header row
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)
                cell.fill = cell.fill.copy(fgColor="DBEAFE")

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
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            # Freeze top row
            worksheet.freeze_panes = 'A2'

        return True

    except Exception as e:
        print(f"Error generating deliveries Excel: {e}")
        return False
