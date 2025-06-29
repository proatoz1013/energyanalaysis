"""
Data Upload Component for Chiller Plant Energy Dashboard

Handles file upload functionality for Excel and CSV files.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

def handle_file_upload():
    """
    Handle file upload with support for multiple formats.
    
    Returns:
        uploaded_file: Streamlit UploadedFile object or None
    """
    st.markdown("### 📁 Upload Your Chiller Plant Data")
    
    # File upload widget
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your chiller plant data in CSV or Excel format"
    )
    
    if uploaded_file is not None:
        # Display file information
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }
        
        with st.expander("📋 File Information", expanded=False):
            for key, value in file_details.items():
                st.text(f"{key}: {value}")
    
    return uploaded_file

def display_upload_status(df, filename):
    """
    Display upload status and basic file information.
    
    Args:
        df (pandas.DataFrame): The uploaded dataframe
        filename (str): Name of the uploaded file
    """
    st.success(f"✅ File '{filename}' uploaded successfully!")
    
    # Display basic statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Rows", f"{len(df):,}")
    
    with col2:
        st.metric("📋 Columns", f"{len(df.columns)}")
    
    with col3:
        numeric_cols = df.select_dtypes(include=['number']).columns
        st.metric("🔢 Numeric Columns", f"{len(numeric_cols)}")
    
    # Show column list
    with st.expander("📝 Column Names", expanded=False):
        col_types = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            if df[col].dtype in ['int64', 'float64']:
                col_type = "🔢 Numeric"
            elif df[col].dtype == 'object':
                col_type = "📝 Text"
            elif 'datetime' in dtype:
                col_type = "📅 DateTime"
            else:
                col_type = "❓ Other"
            col_types.append({"Column": col, "Type": col_type, "Data Type": dtype})
        
        col_df = pd.DataFrame(col_types)
        st.dataframe(col_df, use_container_width=True)

def save_uploaded_file(uploaded_file, upload_dir="../data/uploads/"):
    """
    Save uploaded file to the uploads directory.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        upload_dir (str): Directory to save the file
        
    Returns:
        str: Path to the saved file
    """
    # Create upload directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(uploaded_file.name)[0]
    extension = os.path.splitext(uploaded_file.name)[1]
    unique_filename = f"{base_name}_{timestamp}{extension}"
    
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def validate_file_format(uploaded_file):
    """
    Validate the uploaded file format and basic structure.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    validation_result = {
        'valid': True,
        'errors': []
    }
    
    # Check file extension
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_extension not in allowed_extensions:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Unsupported file format: {file_extension}")
        return validation_result
    
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)
        
        # Try to read the file with proper error handling
        if file_extension == '.csv':
            try:
                df = pd.read_csv(uploaded_file)
            except pd.errors.EmptyDataError:
                validation_result['valid'] = False
                validation_result['errors'].append("CSV file is empty")
                return validation_result
            except pd.errors.ParserError:
                validation_result['valid'] = False
                validation_result['errors'].append("CSV file has parsing errors")
                return validation_result
        else:
            try:
                df = pd.read_excel(uploaded_file)
            except Exception as e:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Excel file error: {str(e)}")
                return validation_result
        
        # Check if file has data
        if len(df) == 0:
            validation_result['valid'] = False
            validation_result['errors'].append("File is empty")
        
        # Check if file has columns
        if len(df.columns) == 0:
            validation_result['valid'] = False
            validation_result['errors'].append("File has no columns")
        
        # Check for minimum number of numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) < 1:
            validation_result['valid'] = False
            validation_result['errors'].append("File must have at least 1 numeric column for analysis")
        
        # Reset file pointer for next read
        uploaded_file.seek(0)
            
    except Exception as e:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Error reading file: {str(e)}")
        # Reset file pointer even on error
        try:
            uploaded_file.seek(0)
        except:
            pass
    
    return validation_result

def render_data_upload():
    """
    Render the data upload interface.
    
    Returns:
        pandas.DataFrame or None: The uploaded and processed dataframe
    """
    st.markdown("### 📁 Upload Your Chiller Plant Data")
    
    # File upload widget
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your chiller plant data in CSV or Excel format"
    )
    
    if uploaded_file is not None:
        # Display file information
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }
        
        with st.expander("📋 File Information", expanded=False):
            for key, value in file_details.items():
                st.text(f"{key}: {value}")
        
        # Reset file pointer before validation
        uploaded_file.seek(0)
        
        # Validate file format
        validation = validate_file_format(uploaded_file)
        
        if not validation['valid']:
            st.error("❌ File validation failed:")
            for error in validation['errors']:
                st.error(f"• {error}")
            return None
        
        # Reset file pointer again before reading
        uploaded_file.seek(0)
        
        try:
            # Read the file with better error handling
            if uploaded_file.name.endswith('.csv'):
                # Try reading CSV with different parameters
                try:
                    df = pd.read_csv(uploaded_file)
                except pd.errors.EmptyDataError:
                    st.error("❌ The CSV file is empty or has no data rows.")
                    return None
                except pd.errors.ParserError as e:
                    st.error(f"❌ Error parsing CSV file: {str(e)}")
                    st.info("💡 Try saving your file with UTF-8 encoding or check for formatting issues.")
                    return None
                except Exception as e:
                    # Try with different encoding
                    try:
                        uploaded_file.seek(0)  # Reset file pointer
                        df = pd.read_csv(uploaded_file, encoding='latin-1')
                        st.warning("⚠️ File read with latin-1 encoding. Some characters might appear differently.")
                    except Exception as e2:
                        st.error(f"❌ Error reading CSV file: {str(e)}")
                        st.info("💡 Please check that your file contains valid data with proper column headers.")
                        return None
            else:
                # Handle Excel files
                try:
                    df = pd.read_excel(uploaded_file)
                except Exception as e:
                    # Try reading the first sheet explicitly
                    try:
                        uploaded_file.seek(0)  # Reset file pointer
                        df = pd.read_excel(uploaded_file, sheet_name=0)
                    except Exception as e2:
                        st.error(f"❌ Error reading Excel file: {str(e)}")
                        st.info("💡 Please ensure your Excel file has data and is not corrupted.")
                        return None
            
            # Additional validation after reading
            if df.empty:
                st.error("❌ The uploaded file contains no data.")
                return None
            
            if len(df.columns) == 0:
                st.error("❌ The uploaded file has no columns.")
                return None
            
            # Check for columns with meaningful names (not just 'Unnamed')
            unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed')]
            if len(unnamed_cols) == len(df.columns):
                st.warning("⚠️ All columns appear to be unnamed. Please ensure your file has proper column headers.")
                st.info("💡 The first row should contain column names.")
            
            # Display upload status
            display_upload_status(df, uploaded_file.name)
            
            return df
            
        except Exception as e:
            st.error(f"❌ Unexpected error reading file: {str(e)}")
            st.info("""
            💡 **Troubleshooting tips:**
            - Ensure your file is not empty
            - Check that the first row contains column headers
            - Verify the file is not corrupted
            - Try saving as CSV with UTF-8 encoding
            """)
            return None
    
    else:
        st.info("👆 Please upload a CSV or Excel file to begin")
        return None