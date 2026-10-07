# **Chicago Crime Analysis Dashboard**

An interactive, production-grade analytics web application built with **Streamlit**, **Pandas**, and **Plotly** to visualize and analyze historical crime patterns across Chicago.  
This dashboard implements all ground rules, KPIs, and visualization specifications defined in the Chicago Crimes Analysis Competition Handout.

## **📌 Dashboard Overview**

The application provides an executive view of Chicago crime data, featuring:

* **8 High-Level KPI Metric Cards** summarizing overall volume, arrest efficiency, and crime characteristics.  
* **10 Visual Analyses** covering temporal patterns, crime classification splits, geographic district rankings, and high-density risk matrices.  
* **Interactive Filtering System** allowing multi-select slicing by primary crime type and police district, with a toggle between **Interactive Sliced View** and **Competition Baseline View** (Ground Rule 3).  
* **Transparent Assumptions Box** detailing time-of-day bins, seasonal groupings, and statutory offense categories.

## **📊 Features & Handout Solutions**

### **Section A: KPI Metric Cards (K1 – K8)**

* **K1. Total Crimes**: Total row count across the dataset.  
* **K2. Arrest Rate %**: Total arrests divided by total crimes $\left({\frac{Arrests}{TotalCrimes}\times 100}\right)$, benchmarked against the worked example.  
* **K3. Domestic Crime %**: Proportion of offenses flagged as domestic incidents.  
* **K4. Unique Crime Types**: Count of distinct primary crime classifications.  
* **K5. Crimes in 2016**: Incident volume isolated for the 2016 calendar year.  
* **K6. Average Monthly Crimes**: Average monthly incident volume across the 28-month evaluation window (April 2015 to July 2017).  
* **K7. Night-Time Crime %**: Percentage of crimes committed between 00:00 and 05:59.  
* **K8. Violent Crime %**: Percentage of offenses classified under violent crimes.

### **Section B: Visual Analytics (Q1 – Q10)**

| Question | Chart Type | Description | Preview |
| :---- | :---- | :---- | :---- |
| **Q1** | Line Chart with Markers | Monthly crime volume trend from April 2015 to July 2017 (28 months) |  |
| **Q2** | Column / Bar Chart | Distribution across days of the week, sorted chronologically (Monday to Sunday) |  |
| **Q3** | Column / Bar Chart | Distribution across times of day, ordered chronologically (Night, Morning, Afternoon, Evening) |  |
| **Q4** | Donut Chart | Seasonal crime distribution isolated strictly to the year 2016 |  |
| **Q5** | Donut Chart | Proportion of offenses categorized as **Violent**, **Property**, or **Other** |  |
| **Q6** | Column / Bar Chart | Arrest rate percentage across each chronological time-of-day period |  |
| **Q7** | Horizontal Bar Chart | Top 10 primary crime types by total volume, sorted from highest to lowest |  |
| **Q8** | Horizontal Bar Chart | Top 5 primary crime types specifically for domestic incidents |  |
| **Q9** | Dual-Axis Combo Chart | Top 10 police districts by total crime volume (bars) and their arrest rate % (secondary line) |  |
| **Q10** | Heatmap Matrix | 7×4 cross-tabulation matrix of Day of Week vs. Time of Day with density labels |  |

## **📥 Dataset Access & Download**

The project evaluates historical Chicago crime records. The dataset can be accessed and downloaded via Google Drive\[cite: 1\]:

* **Dataset URL**: [Google Drive Crime Dataset](https://docs.google.com/spreadsheets/d/1AwD-nwf3I2LuHUTIBV1JrknORZHT6Ef9/edit?usp=sharing&ouid=113168550696612522845&rtpof=true&sd=true)\[cite: 1\]

### **Option 1: Direct Browser Download**

> 1. Open the [dataset spreadsheet link](https://docs.google.com/spreadsheets/d/1AwD-nwf3I2LuHUTIBV1JrknORZHT6Ef9/edit?usp=sharing&ouid=113168550696612522845&rtpof=true&sd=true) in your browser\[cite: 1\].  
> 2. Click **File** $\rightarrow$ **Download** $\rightarrow$ **Microsoft Excel (.xlsx)** or **Comma Separated Values (.csv)**.  
> 3. Save the file into the root folder of this repository as:  
   * Google Drive Crime Dataset.xlsx or Crimes Dataset Clean.csv.

### **Option 2: Direct Export via URL**

Download directly via the export link:

Plaintext  
https\://docs.google.com/spreadsheets/d/1AwD-nwf3I2LuHUTIBV1JrknORZHT6Ef9/export?format=xlsx

### **Option 3: Terminal Download (using curl or wget)**

Bash  
curl \-L \-o "Google Drive Crime Dataset.xlsx" "https\://docs.google.com/spreadsheets/d/1AwD-nwf3I2LuHUTIBV1JrknORZHT6Ef9/export?format=xlsx"

*(Note: The app also provides a drag-and-drop file uploader in the sidebar, so you can upload the file directly through the UI).*

## **📂 Repository Structure**

Plaintext  
├── app.py                                                \# Main Streamlit application  
├── requirements.txt                                      \# Project dependencies  
├── README.md                                             \# Project documentation  
├── Google Drive Crime Dataset.xlsx                       \# Crime records (place here)  
│  
├── Dashboard.png                                         \# Complete dashboard preview  
├── q1-monthly-crime-count-apr-2015-jul-2017.png          \# Exported Q1 visual  
├── q2-number-of-crimes-by-day-of-the-week.png            \# Exported Q2 visual  
├── q3-crimes-by-time-of-day-chronological-o.png          \# Exported Q3 visual  
├── q4-crimes-by-season-year-2016-only.png                \# Exported Q4 visual  
├── q5-share-of-crime-categories-violent-pro.png          \# Exported Q5 visual  
├── q6-arrest-rate-for-each-time-of-day.png               \# Exported Q6 visual  
├── q7-top-10-crime-types-by-total-incidents.png          \# Exported Q7 visual  
├── q8-top-5-domestic-crime-types.png                     \# Exported Q8 visual  
├── q9-top-10-police-districts-volume-arrest.png          \# Exported Q9 visual  
└── q10-crime-density-heatmap-day-of-week-vs.png          \# Exported Q10 visual

## **⚙️ Installation & Local Setup**

### **1\. Clone the Repository**

Bash  
git clone https\://github.com/\<your-username\>/Chicago-Crime-Dashboard.git  
cd Chicago-Crime-Dashboard

### **2\. Create and Activate a Virtual Environment**

#### **On Windows:**

PowerShell  
\# Create venv  
python \-m venv venv

\# Activate venv  
.\\venv\\Scripts\\Activate.ps1

*If you encounter an execution policy error on PowerShell, run:*  
Set-ExecutionPolicy \-Scope Process \-ExecutionPolicy Bypass

#### **On macOS / Linux:**

Bash  
\# Create venv  
python3 \-m venv venv

\# Activate venv  
source venv/bin/activate

### **3\. Install Dependencies**

Always use python \-m pip to ensure packages are installed directly into your active virtual environment:

Bash  
python \-m pip install \-r requirements.txt

### **4\. Run the Dashboard**

Launch Streamlit using the virtual environment's Python module:

Bash  
python \-m streamlit run app.py

The application will open automatically in your browser at http\://localhost:8501.

## **📐 Ground Rules & Business Logic**

The dashboard adheres strictly to the competition ground rules:

> 1. **Time of Day Definitions**:  
   * **Night**: 00:00 – 05:59  
   * **Morning**: 06:00 – 11:59  
   * **Afternoon**: 12:00 – 17:59  
   * **Evening**: 18:00 – 23:59  
> 2. **Season Classifications**:  
   * **Winter**: December, January, February  
   * **Spring**: March, April, May  
   * **Summer**: June, July, August  
   * **Fall**: September, October, November  
> 3. **Crime Category Mappings**:  
   * **Violent Crime**: Assault, Battery, Robbery, Homicide, Criminal Sexual Assault, Kidnapping  
   * **Property Crime**: Theft, Burglary, Motor Vehicle Theft, Criminal Damage, Arson  
   * **Other Crime**: All remaining offense types  
> 4. **Specific Time Windows**:  
   * **Q1 & K6**: Strictly calculated over the 28-month range from **April 2015 to July 2017**.  
   * **Q4 & K5**: Isolated strictly to calendar year **2016**.

## **🛠️ Built With**

* [Streamlit](https://streamlit.io/) – Modern web framework for data applications.  
* [Pandas](https://pandas.pydata.org/) – High-performance vectorized data manipulation.  
* [Plotly](https://plotly.com/python/) – Interactive, publication-ready data visualizations.  
* [OpenPyXL](https://openpyxl.readthedocs.io/) – Excel workbook parser.