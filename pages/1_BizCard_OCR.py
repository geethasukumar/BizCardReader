# import libraries
import easyocr
import pandas as pd
import re
import streamlit as st
import numpy as np
from PIL import Image
import io
import mysql.connector
from mysql.connector import Error
import base64

    

class bizcard:
    def __init__(self, p_img):
    
        self.uploaded_img=p_img
        self.data = {"company_name" : [],
            "card_holder" : [],
            "designation" : [],
            "mobile_number" :[],
            "email" : [],
            "website" : [],
            "area" : [],
            "city" : [],
            "state" : [],
            "pin_code" : [],        
            "image" : ''
        }
        self.img_result=[]
        self.mysql_db_connect()
    

    # MySQL DB connect
    def mysql_db_connect(self):
       
        hostname= "localhost"
        database= "bizcard_ocr"
        username= "root"
        password= ""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=hostname,
                database=database,
                user=username,
                password=''
            )
            if connection.is_connected():
              
                self.connection = connection
        except Error as e:
            st.write(f"Error: {e}")
            st.write('Error mysql_db_connect - MYSQL DB connection failed!!')
           


    
    # Doing OCR. Get bounding boxes.
    def read_image(self):
        self.pil_image = Image.open(self.uploaded_img)
   
     
     # Convert the PIL image to a NumPy array
        img_np = np.array(self.pil_image)
        
        reader = easyocr.Reader(['en'])
        extracted_text = reader.readtext(img_np)
        
        for result in extracted_text:
            self.img_result.append(result[1])



    # convert the image to bytes to store in blob column
    def image_to_byte_array(self):
        img_byte_array = io.BytesIO()
        
        self.pil_image.save(img_byte_array, format='PNG')  # Change 'JPEG' to the format you desire (e.g., PNG)
        encoded_image = base64.b64encode(img_byte_array.getvalue())
      
        self.image_byte=encoded_image
  
    
    
    # Save data to DB
    def save_to_db(self,edited_df):
        try:
            cursor = self.connection.cursor()
            
            query = "INSERT INTO bizcard_data (company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,card_image) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            
            card_values = (str(edited_df['company_name'][0]),str(edited_df['card_holder'][0]),str(edited_df['designation'][0]),str(edited_df['mobile_number'][0]),str(edited_df['email'][0]),str(edited_df['website'][0]),str(edited_df['area'][0]),str(edited_df['city'][0]),str(edited_df['state'][0]),str(edited_df['pin_code'][0]),edited_df['image'][0])
            cursor.execute(query, card_values)
            self.connection.commit()
            st.write("Business Card Data saved to the database successfully!")
           
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
       
    

   
       
        
    # read data from the ocr reader object and store in the array
    def get_data(self):
    
        self.image_to_byte_array() # convert the images to bytes for saving it to blob
         
        for ind,i in enumerate(self.img_result):
          
            # To get WEBSITE_URL
            if "www " in i.lower() or "www." in i.lower():
                self.data["website"].append(i)
            elif "WWW" in i:
                self.data["website"] = self.img_result[4] +"." + self.img_result[5]

            # To get EMAIL ID
            elif "@" in i:
                self.data["email"].append(i)

            # To get MOBILE NUMBER
            elif "-" in i:
                self.data["mobile_number"].append(i)
                if len(self.data["mobile_number"]) ==2:
                    self.data["mobile_number"] = ", ".join(self.data["mobile_number"])

            # To get COMPANY NAME  
            elif ind == len(self.img_result)-1:
                self.data["company_name"].append(i)

            # To get CARD HOLDER NAME
            elif ind == 0:
                self.data["card_holder"].append(i)

            # To get DESIGNATION
            elif ind == 1:
                self.data["designation"].append(i)

            # To get AREA
            if re.findall('^[0-9].+, [a-zA-Z]+',i):
                self.data["area"].append(i.split(',')[0])
            elif re.findall('[0-9] [a-zA-Z]+',i):
                self.data["area"].append(i)

            # To get CITY NAME
            match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
            match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
            match3 = re.findall('^[E].*',i)


            if match1:
                self.data["city"].append(match1[0])
            elif match2:
                self.data["city"].append(match2[0])
            elif match3:
                self.data["city"].append(match3[0])


            # To get STATE
            state_match = re.findall('([a-zA-Z]+) ([0-9]+)$',i)


            if state_match:
                self.data["state"].append(state_match[0][0])
                self.data["pin_code"].append(state_match[0][1])
            elif matches := re.findall('^([0-9]+),+ ([a-zA-Z]+);',i):

                self.data["pinself._code"].append(matches[0][0])

            if not self.data['state']:

                state_match1 = re.findall('^(.+?)(;|,) ([a-zA-Z]+)(,|;)$',i)
                if state_match1:
                    self.data["state"].append(state_match1[0][2])

            if len(self.data["state"])== 2:
                self.data["state"].pop(0)
                           
            # To get PINCODE        
            if len(i)>=6 and i.isdigit():
              
               self.data["pin_code"].append(i)
            
            self.data['image']=self.image_byte
            

    # convert DF to DataFrame
    def convert_to_df(self):
        self.df = pd.DataFrame(self.data)
        
        
        
        
        
# Main program that creates the obj, dataframe and show the data    
def main():

    st.title ("BizCardX: Business Card Data with OCR")
    st.markdown("By Geetha Sukumar")
    m = st.markdown("""
                    <style>
                    div.stButton > button:first-child {
                        background-color: #42c2f5;
                        color:#ffffff;
                    }


                    </style>""", unsafe_allow_html=True)
    uploaded_image = st.file_uploader("Upload a Business Card", type=["jpg", "jpeg", "png"])
    if "filename" not in st.session_state: 
        st.session_state.filename= ''
        
    #if "bizcard_obj" not in st.session_state:
        #bizcard_obj = bizcard('C:/Users/rgkri/OneDrive/Geetha/GUVI/project/Bizcard_Reader/data/2.png')
        
    with st.spinner():   
        if uploaded_image and uploaded_image.name != st.session_state.filename :
            # Display the uploaded image
            #st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
          
            st.session_state.filename = uploaded_image.name
            
            bizcard_obj = bizcard(uploaded_image)
            st.session_state.bizcard_obj = bizcard_obj

            bizcard_obj.read_image()
         
            bizcard_obj.get_data()
            bizcard_obj.convert_to_df()
            st.session_state.df=bizcard_obj.df



        if "df" in st.session_state:
        
            # Using hide Index
            st.session_state.df.style.hide_index()

            edited_df = st.data_editor(st.session_state.df.loc[:, st.session_state.df.columns != 'image'], hide_index=True) # Editable Data Grid
        

            col1, col2 = st.columns(2)
            with col1:
                st.empty()
                st.image(st.session_state.bizcard_obj.pil_image, caption='Business Card')
            with col2:
                 if st.button("Save Data"):
                    new_df = pd.DataFrame(edited_df)
            
                    new_df['image']=st.session_state.df.loc[:,st.session_state.df.columns == 'image']
                    
                    st.session_state.bizcard_obj.save_to_db(new_df)
             




if __name__ == "__main__":
    main()