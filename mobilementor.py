import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#write some strings using titles and text
st.title("Mobile Mentor")
st.header("Your Mobile Phone Comparison Tool")
st.write(":wave: Hello :wave:")
st.write(":book: Welcome to my coding project in the course 'Skills: Programming - Introduction Level (3,793,1.00)'")
st.write(":book: This web application can compare any mobile phone from a dataset of 8775 entries. The full documentation, code and dataset are provided with the submission of the project")

#set pathfile and read it, save it as "df"
file_path = "mobiles.csv"
df = pd.read_csv(file_path)

###function to modify the dataframe in the very beginning
def modify_df(df):

    ###adjust the dataframe to fit the project needs
    #make sure only entries with a Product Name exist
    df = df.dropna(subset=["Product Name"])
    
    #convert "Price in India" Column to "Price in CHF"
    df["Price in India"] = df["Price in India"].str.replace("₹ ", "").astype(str) #remove indian currency
    df["Price in India"] = df["Price in India"].str.replace(",", "").astype(float) #remove commas and convert to numeric
    df["Price in India"] = df["Price in India"] * 0.011 #convert values into swiss currency
    df.rename(columns={"Price in India": "Price in CHF"}, inplace=True) #rename column

    #create new column for the Overall Rating , which is a product from other existing columns
    df["Overall Rating"] = (df["1 Stars"] * 1 + df["2 Stars"] * 2 + df["3 Stars"] * 3 + df["4 Stars"] * 4 + df["5 Stars"] * 5)/(df["1 Stars"] + df["2 Stars"] + df["3 Stars"] + df["4 Stars"] + df["5 Stars"])

    #create new column for the Main Camera, which is part of an existing column, and modify it
    df["Main Camera (megapixel)"] = df["Rear camera"].str.split("-").str[0] #split the text in the column Rear Camera and take the first part of it
    df["Main Camera (megapixel)"] = df["Main Camera (megapixel)"].str.replace("Yes", "0").astype(str) #replace wrong values
    df["Main Camera (megapixel)"] = df["Main Camera (megapixel)"].str.replace("No", "0").astype(str) #replace wrong values
    df["Main Camera (megapixel)"] = df["Main Camera (megapixel)"].str.replace("nan", "0").astype(str) #replace wrong values
    
    #create new column for the Amount of Pixels, which is a product of an existing column
    df["Resolution"] = df["Resolution"].str.replace(",", "").astype(str) #remove any commas
    df["Resolution"] = df["Resolution"].str.replace("(", "").astype(str) #remove any brackets
    df["Resolution"] = df["Resolution"].str.replace("pi", "").astype(str) #remove any letters
    df["Amount of Pixels"] = df["Resolution"].str.split("x").str[0].astype(float) * df["Resolution"].str.split("x").str[1].astype(float) #split the string at "x" and multiply the two parts
    
    #create new column for the points
    df["Points"] = 0

    #fill NaN values with 0
    df.fillna(0, inplace=True)
    
    return df

###Function to display images of the selected devices
def display_images(dataframe): 
    
    #Create a toggle to display the images
    on2 = st.toggle("See images of your selected mobile phones")
    
    #check if the toggle button is on
    if on2:
       
        #go through every item in the selection and display it in a simple table (go through the picture url and the product name with a for loop)
        for image_path, device_name in zip(dataframe["Picture URL"], dataframe["Product Name"]):
            
            #create two columns with the ratio of 1:2 
            col1, col2 = st.columns([1, 2])
            
            #fill the first and second column
            with col1:
                
                #create an image using the picture url from the dataset
                st.image(image_path, width=200)
                
            with col2:
            
                #write the name of the device using the dataset
                st.write(device_name)
 
###Function to generate and display the charts
def create_charts(dataframe, ranked_dataframe, category_dataframe):

    #Create a bar chart for each category
    #Price comparison
    chart_price = alt.Chart(dataframe).mark_bar().encode(
        y="Product Name:N", #Take the products name as a nominal value
        x="Price in CHF:Q", #Take the Price as a quantitive value
        color=alt.value("red") #Set color
    )

    #Rating comparison
    chart_rating = alt.Chart(dataframe).mark_bar().encode(
        y="Product Name:N",
        x="Overall Rating:Q",
        color=alt.value("yellow") 
    )

    #Camera comparison
    chart_main_camera = alt.Chart(dataframe).mark_bar().encode(
        y="Product Name:N",
        x="Main Camera (megapixel):Q",
        color=alt.value("blue")
    )
    
    #Resolution comparison
    chart_resolution = alt.Chart(dataframe).mark_bar().encode(
        y="Product Name:N",
        x="Amount of Pixels:Q",
        color=alt.value("grey")
    )
    
    #Battery comparison
    chart_battery = alt.Chart(dataframe).mark_bar().encode(
        y="Product Name:N",
        x="Battery capacity (mAh):Q",
        color=alt.value("green")
    )
    
    #Points comparison
    chart_best_product = alt.Chart(ranked_dataframe).mark_bar().encode(
        y=alt.Y("Product Name:N", sort="-x"), #sort descending, highest value on top
        x="Points:Q",
        color=alt.value("pink")
    )

    #Create a spider chart to inspect the strengths and the points
    #Melt the dataframe into a long format, so the spider chart can read and display it
    long_df = category_dataframe.melt(id_vars=["Product Name"], 
                                      var_name="Category", value_name="Points")
                                      
    #Look for the highest amount of points in the comparison
    max_points = long_df["Points"].max()
  
    #Create a spider chart to display the strengths of the devices using the calculated points
    fig = px.line_polar(long_df, r="Points", theta="Category", color="Product Name", line_close=True)

    #Update the plot
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  #set transparent background
        plot_bgcolor="rgba(0,0,0)",  #set transparent background
        polar=dict(
            radialaxis=dict(
                color="black",  #set axis color
                range=[0, max_points+0.5],  #set axis range to give the plotpoints some space
            )))

    #the spider chart should be filled with the color, not just outline
    for trace in fig.data:
        trace.update(fill="toself")

    #Display charts and write text    
    st.subheader(":100: Best Mobile Phone :100:")
    st.write(f":reminder_ribbon: The best mobile phone in your comparison is: {ranked_dataframe['Product Name'].iloc[0]}")
    st.altair_chart(chart_best_product, use_container_width=True) #display chart
    st.write(":mag: For further insights have a look at the different comparisons")

    #create two columns with the ratio of 1:1
    col3, col4 = st.columns([1, 1])
    
    #fill the columns with a small title and then display the graph created before
    with col3:
        st.write(":money_with_wings: Price :money_with_wings:") #title
        st.altair_chart(chart_price, use_container_width=True) #display chart
    with col4:
        st.write(":star: Overall Rating :star:")
        st.altair_chart(chart_rating, use_container_width=True)  
    with col3:
        st.write(":camera: Main Camera :camera:")
        st.altair_chart(chart_main_camera, use_container_width=True)       
    with col4:
        st.write(":eye: Amount of Pixels :eye:")
        st.altair_chart(chart_resolution, use_container_width=True)
    with col3:
        st.write(":battery: Battery Capacity (mAh):battery:")
        st.altair_chart(chart_battery, use_container_width=True)
    
    st.write(":mag: Below you can inspect the different strengths of the devices") #another section
    st.plotly_chart(fig, use_container_width=True) #last chart
    
###Function to calculate the points
def calculate_points(dataframe):

    categories = ["Product Name"] + rating_categories
    category_points = dataframe[categories]

    #go through each rating category
    for column in rating_categories:
       
        #make sure its a float
        dataframe[column] = dataframe[column].astype(float)
       
        #rank the device in the category with pandas rank function
        #make an exception for the category price, here its better to have a low price
        if column == "Price in CHF":          
            ranks = dataframe[column].rank(ascending=True, method="max") #if ascending is true, the lower the value the better - if methode is max, same ranks receive the higher rank
        else:
            ranks = dataframe[column].rank(ascending=False, method="max") #if ascending is false, the higher the value the better - if methode is max, same ranks receive the higher rank
        
        #Add points depending on the rank to the devices
        #Example: 3 items are compared, the item with the best camera is rank 1
        #We subtract its rank from the size (3-1) and add 1
        #The item is the winner of three devices, so it receives 3 points
        dataframe["Points"] += ranks.apply(lambda x: num_items - int(x) + 1) #for every item in the dataset, take the size of the selection, subtract its rank and add 1 to calculated points.
        category_points[column] = ranks.apply(lambda x: num_items - int(x) + 1)
        
    #Create a new dataframe that shows the ranked devices, higher amounts of points are on top
    ranked_dataframe = dataframe.sort_values(by="Points", ascending=False)      
    return ranked_dataframe, category_points

#modify dataframe with function
df = modify_df(df)

#create a toggle to display the full dataframe
on1 = st.toggle("Click this toggle to see the full dataframe used in this project")

#check if toggle button is on
if on1:
    
    #write some stuff to explain things
    st.write(":book: The original dataset is provided with the project's submission. Below you can see the modified version of the dataframe used in this project. ")
    st.write(":book: This dataset was customised to fit the project's needs. The new dataset contains 'Price in CHF' instead of 'Price in India' and in addition has the columns 'Overall Rating', 'Amount of Pixels', 'Main Camera (megapixel)' and 'Points' .")
    st.write(":book: To look up one specific row, please use the search bar below and enter any name, e. g. Samsung Galaxy S20+.")
    
    #create a searchbar
    search1 = st.text_input(
                        "Search for a specific mobile phone", #title of the searchbar
                        value="", #value of the searchbar
                        placeholder="e.g. Samsung Galaxy S20+ (8GB RAM, 128GB) - Cosmic Black", #hint of the searchbar
                        key="uniquesearch1") #unique key of the searchbar
    
    #create a multiselectionbar
    options1 = st.multiselect(
                        "Please select the columns which should be displayed", #title of the multiselectionbar
                        df.columns, #options of the multiselectionbar
                        ["Product Name", "Price in CHF", "Overall Rating", "Amount of Pixels", "Main Camera (megapixel)", "Points"], #pre-selected options of the multiselectionbar
                        key="uniqueoption1") #unique key of the multiselectionbar
    
    #create a filtered dataframe, containing every item that contains the string from the searchbar, display it
    filtered_df1 = df[df["Product Name"].str.contains(search1, case=False, na=False)] #not case-sensitive
    st.write(filtered_df1[options1])

#create new section
st.divider()
st.header("Compare the mobile phones now")
st.write(":arrow_right: Select the mobile phones you want to compare. Choose as many as you want.")

#create a multiselectionbar
device_selection = st.multiselect("Select a mobile phone", #title of the multiselectionbar
                       df["Product Name"], #options of the multiselectionbar
                       key="uniqueoption2") #unique key of the multiselectionbar

#define the columns of the dataframe that will be compared
rating_categories = ["Price in CHF", "Overall Rating", "Main Camera (megapixel)", "Amount of Pixels", "Battery capacity (mAh)"]

#create a filtered dataframe, where the products name matches with an item of the selection
selection_df = df[df["Product Name"].isin(device_selection)]

#save the size of the selection for the ranking system
num_items = len(selection_df)

#Check if there is a selection
if device_selection != []:
    
    #create a toggle to see the dataframe of the selected devices
    on3 = st.toggle("See the selected mobile phones in the dataset")
    
    #check if the toggle is on
    if on3:
        
        #create a multiselectionbar
        options3 = st.multiselect(
            "Please select the columns which should be displayed", #title
            df.columns, ["Product Name"] + rating_categories, key="uniqueoption3") #options, preselected options and a unique key
        
        #display dataframe    
        st.write(selection_df[options3])

    #execute all functions and do the comparison
    display_images(selection_df)
    ranked_df, category_points_df = calculate_points(selection_df)
    create_charts(selection_df, ranked_df, category_points_df) 

#create last section    
st.divider()
st.header("Further analysis")

#create toggle
on4 = st.toggle("Let's analyse the distribution of mobile phone characteristics of different brands")

if on4: #check if toggle is on

    #some text
    st.write("In this section you can see how the brands design their devices and how the specifications are distributed in the individual categories. The graph shows how often a value is chosen by the manufacturer when designing a product ")

    #create two selection bars to select a brand and a category
    selected_option = st.selectbox("Please select the brand you want to analyse", df["Brand"].unique())
    selected_category = st.selectbox("Please select the category you want to analyse", rating_categories)
    
    #filter the df for only items with the selected brand 
    analyzing_df = df[df["Brand"].str.contains(selected_option, case=False, na=False)]
    
    #make sure every value is treated as a float
    analyzing_df[selected_category] = analyzing_df[selected_category].astype(float)
    
    #filter the df so only values larger than 0 will be taken
    analyzing_df = analyzing_df[analyzing_df[selected_category] > 0]
    
    #sort the df in ascending order
    analyzing_df = analyzing_df.sort_values(by=selected_category)
    
    #count how often a value appears and save it in a new df
    analyzing_df_counts = analyzing_df[selected_category].value_counts()

    #display the bar chart
    st.bar_chart(analyzing_df_counts)
    
    #receive some information bout the dataframe
    described_values = analyzing_df[selected_category].describe()
    
    #give the user the infos, write the min, max and mean value of the set
    st.write(f" The devices from the brand '{selected_option}' have a range between {described_values[3]} (min) and {described_values[7]} (max) in the category '{selected_category}' with the average value of {described_values[1]}.")
