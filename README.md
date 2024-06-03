# TECHIN510_RustKiller
🌾 A web app to detect rust disease in wheat, including data analysis, data visualization, and an AI chatbot.  

Web app:  https://farmbeats.streamlit.app/  
Youtube: https://youtu.be/Fxh6IdDXCK0



### Technologies used
```bash
Azure Blob, Azure Table
Streamlit App
Raspiberry Pi4
Digital Signal Process
```

### What problems you are trying to solve

Our project aims to address the problem of efficiently detecting and monitoring stripe rust (yellow rust) disease in wheat crops. 
After conducting research, we found that stripe rust spreads rapidly under suitable temperature and humidity conditions.
Our solution will enable farmers to remotely monitor their wheat crops, receive timely datas and alerts about disease outbreaks, and take proactive measures to alleviate the impact of the disease.


### How to run
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
source venv/bin/activate

# Run the app
streamlit run app.py
```

### Reflections
#### What you learned
- We learned how to use and connect different platforms, Azure and the Streamlit app, to store and visualize data. 
- Additionally, we learned how to use a generative AI API to create a chatbot that accesses the database and answers users' questions.
- We learned to build the web with several pages by putting them into ```pages``` folder
- We learned to use ```update_status``` to detect changes in the "Status" column and update Azure Table. Realize the interaction between user end and database.


#### What questions/problems did you face?
- For the generative AI API, I initially tried using the OpenAI API. However, I encountered problems connecting to OpenAI. As a result, I switched to using the Google Gemini API instead.
- I designed and developed a popup to inform users of potential rust occurrences. However, when I wanted to enhance it by allowing users to cancel the alert, I realized that without a database, the alert would reappear upon refreshing the webpage even if it was canceled once. Due to time and technical constraints, I decided to skip this feature for now but plan to address it in the future.

