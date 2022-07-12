import streamlit as st

import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# IMPORT DATASET
@st.cache(allow_output_mutation=True)
def delay():
  data = pd.read_excel("get_around_delay_analysis.xlsx")
  return data

data = delay()

# IMPORT VARIABLES

# Show number of cars
cars = len(data['car_id'].unique())
# Show number of rentals
rentals = len(data['rental_id'].unique())
# Show delay at checkout mean
delay_mean = data.delay_at_checkout_in_minutes.mean()
# Show delay at checkout mean for mobile checkin
data_mobile = data[data.checkin_type =='mobile']
delay_mobile = data_mobile.delay_at_checkout_in_minutes.mean()
# Show delay at checkout mean for connect checkin
data_connect = data[data.checkin_type =='connect']
delay_connect = data_connect.delay_at_checkout_in_minutes.mean()
# Create a new dataframe with a delay at checkout between 12 hours
data_without_outliers = data[(data.delay_at_checkout_in_minutes > -720) & (data.delay_at_checkout_in_minutes < 720)]
# Create dataframe with ratio checkin type
data_ratio_chekin = (data['checkin_type'].value_counts(normalize=True)*100).rename_axis('state').reset_index(name='counts')
# Create new column to show if a car is late or not
data['late'] = data['delay_at_checkout_in_minutes'].apply(lambda x: 'late' if x > 0 else 'in time')
# Delete Nan values
data_clean = data[data["delay_at_checkout_in_minutes"].isna() == False]
# Show numbers of effective rentals in the dataset
effectiv_rentals = data_clean.shape[0]
# Create a dataframe with a ratio of late or in time rentals
data_late_ratio = (data_clean['late'].value_counts(normalize=True)*100).rename_axis('late').reset_index(name='counts')
# Create a dataframe with a ratio of canceled and ended rentals
data_ratio_state = (data['state'].value_counts(normalize=True)*100).rename_axis('state').reset_index(name='counts')
# Create datafrema with only canceled 
data_canceled = data[data["state"] == "canceled"]
# Create column with nan = > 720 minutes
data_canceled['delta'] = data_canceled.time_delta_with_previous_rental_in_minutes.isna().apply(lambda x: x if x == False else '> 720 minutes')
# Create a dataframe with a ratio delta for canceled rentals
data_ratio_delta_canceled_all = (data_canceled.delta.value_counts(normalize=True)*100).rename_axis('delta').reset_index(name='counts')
# Create a dataframe with a ratio delta for canceled rentals with only < 12h delta time
data_ratio_delta_canceled = (data_canceled.time_delta_with_previous_rental_in_minutes.value_counts(normalize=True)*100).rename_axis('delta').reset_index(name='counts')
# Create dataframe with only rentals with time delta with previous < 12 hours
data_canceled_clean = data_canceled[~data_canceled.previous_ended_rental_id.isnull()]
# Create a list of the column time delta
previous_rental = data_canceled_clean["previous_ended_rental_id"]
# Create dataframe with previous rentals in this list
data_previous_rental = data[data["rental_id"].isin(previous_rental)]
### Create a merged dataframe with the previous and next rental
merged_data = data_previous_rental.merge(data, how='inner', left_on='rental_id', right_on='previous_ended_rental_id')
# Drop useless columns
merged_data.drop(['state_x', 'previous_ended_rental_id_x','previous_ended_rental_id_y', 'time_delta_with_previous_rental_in_minutes_x', 'car_id_y', 'delay_at_checkout_in_minutes_y'], axis=1, inplace=True)
# ratio of checkin type for cancelation
data_canceled_ratio_chekin = (merged_data['checkin_type_x'].value_counts(normalize=True)*100).rename_axis('checkin').reset_index(name='counts')
# ratio of lateness for cancelation
data_canceled_ratio_lateness = (merged_data['late_x'].value_counts(normalize=True)*100).rename_axis('lateness').reset_index(name='counts')
# only late cars
data_canceled_late = merged_data[merged_data.delay_at_checkout_in_minutes_x > 0]
# Create treshold
treshold_delay = data_canceled_late.delay_at_checkout_in_minutes_x.quantile(0.80)
# Create dataframe with only previous rental
data_previous_rental = data[~data.previous_ended_rental_id.isnull()]
# Make a list of the column
previous_rental = data_previous_rental["previous_ended_rental_id"]
# Create dataframe with previous rental found 
data_previous_rental = data[data["rental_id"].isin(previous_rental)]
# Create a merged dataframe with the previous and next rental & drop useless columns
merged_data = data_previous_rental.merge(data, how='inner', left_on='rental_id', right_on='previous_ended_rental_id')
merged_data.drop(['state_x', 'previous_ended_rental_id_x','previous_ended_rental_id_y', 'time_delta_with_previous_rental_in_minutes_x', 'car_id_y', 'delay_at_checkout_in_minutes_y'], axis=1, inplace=True)
# Create a copy of the dataframe with only ended
data_merged_ended = merged_data[merged_data["state_y"] == "ended"].copy()
# Select rentals > to the treshold
data_ended_treshold = data_merged_ended[data_merged_ended["time_delta_with_previous_rental_in_minutes_y"] >= treshold_delay]
# Define how many rentals are affected by treshold
Rentals_affected = len(data_merged_ended)-len(data_ended_treshold)
# Define loss for the owners
owners_rentals_loss = 100-(len(data_ended_treshold)*100)/len(data_merged_ended)
# Create ratio of lost and sucessful rentals
ratio_treshold_ended = [(len(data_ended_treshold)*100)/len(data_merged_ended), 100-(len(data_ended_treshold)*100)/len(data_merged_ended)]
# Define graph objects pie chart lables and values
labels = ['sucessful rentals', ' lost rentals']
values = ratio_treshold_ended


def main():
    pages = {
        'EDA': EDA,
        'REPORT': report,
        }

    if "page" not in st.session_state:
        st.session_state.update({
        # Default page
        'page': 'EDA'
        })

    with st.sidebar:
        page = st.selectbox("", tuple(pages.keys()))

    pages[page]()

def EDA():
    st.header('------------  EDA GETAROUND  -------------')

    # Dataset caracteristics
    st.subheader('1 | About the rentals')
    # Show number of cars
    st.write(f'There are {cars} cars in the data set')
    # Show number of rentals
    st.write(f'There are {rentals} rentals in the data set')
    # Show delay at checkout mean
    st.write(f'the average delay at checkout is {round(delay_mean)} minutes')


    # Display delay at checkout in minutes distribution within 12 hours range
    fig = px.histogram(data_without_outliers, x="delay_at_checkout_in_minutes",
                      title = 'Rentals distribution for a delay at checkout in minutes within 12 hours range',
                      color = 'checkin_type',
                      barmode ='group',
                      width= 1000,
                      height = 600
                      ) 
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      xaxis_title = '',
                      yaxis_title = '',
                      template = 'plotly_dark'
                      )
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                      'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )       
    st.plotly_chart(fig)
    st.markdown('The majority of the delay within checkout distribution is between -200 and 200 minutes')

    # Show delay at checkout mean for mobile checkin 
    st.write(f'the average delay at checkout for mobile is {round(delay_mobile)} minutes')
    # Show delay at checkout mean for connect checkin
    st.write(f'the average delay at checkout for connect is {round(delay_connect)} minutes')
    st.markdown('The connect checkin tend to an earlier checkout, probably because only one person is needed to bring back the car')

    # Display ratio of checkin type rentals
    fig = px.pie(data_ratio_chekin,
                values='counts',
                names='state', 
                width= 1000,
                title='Proportion of Mobile and Connect Rentals'
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )    
    st.plotly_chart(fig)
    st.markdown('Checkin type connect represente 20% of the rentals, probably because few cars possess the technology')

    st.subheader('2 | With a cleaning of rentals to keep only those with an effective delay :')
    st.write(f'There are {effectiv_rentals} effective rentals in the data set')

    # piechart for late or in time cars for effective rentals
    fig = px.pie(data_late_ratio,
                values='counts',
                names='late', 
                color ='late',
                title='Proportion of late or in time cars for the checkout',
                width= 1000,
                color_discrete_map={'late':'purple',
                                    'in time':'lightblue'}
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      template = 'plotly_dark' )                
    st.plotly_chart(fig)

    # Histogram for delay at checkout by checkin type
    fig = px.histogram(data_clean, x="late",
                      title = 'Proportion of late or in time cars for the checkout between mobile and connect checkin type',
                      color = 'checkin_type',
                      histnorm= 'percent',
                      barmode ='group',
                      width= 1000,
                      height = 600,
                      text_auto = True
                      )
    fig.update_traces(textposition = 'outside', textfont_size = 15)
    fig.update_layout(title_x = 0.5,
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      yaxis = {'visible': False}, 
                      xaxis = {'visible': True}, 
                      xaxis_title = '',
                      template = 'plotly_dark',
                      )
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                      'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )                                  
    st.plotly_chart(fig)
    st.write(' There is a difference between checkin type probably because mobile type need to give the keys back')

    # Piechart proporion for state of the cars
    fig = px.pie(data_ratio_state,
                values='counts',
                names='state',
                color = 'state',
                width= 1000,
                title='Proportion of ended versus canceled rentals',
                color_discrete_map={'ended':'green',
                                    'canceled':'pink'}
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )    
    st.plotly_chart(fig)

    # histogram for delay at checkout by checkin type
    fig = px.histogram(data, x = "state",
                      title = 'Proportion of canceled or ended rentals between mobile and connect checkin type',
                      color = 'checkin_type',
                      barmode ='group',
                      histnorm = 'percent',
                      width= 1000,
                      height = 600,
                      text_auto = True
                      )       
    fig.update_traces(textposition = 'outside', textfont_size = 15)
    fig.update_layout(title_x = 0.5,
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      yaxis = {'visible': False}, 
                      xaxis = {'visible': True}, 
                      xaxis_title = '',
                      template = 'plotly_dark'
                      )
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                      'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )                    
    fig.update_xaxes(tickfont_size=15)                     
    st.plotly_chart(fig)

    st.subheader('3 | EDA about the canceled rentals')

    st.write(f'There are {len(data_canceled)} canceled rentals')

    # Piechart proporion for delta ratio canceled cars
    fig = px.pie(data_ratio_delta_canceled_all,
                values='counts',
                names='delta',
                color = 'delta',
                color_discrete_map={'> 720 minutes':'brown','false':'white'},
                width= 1000,
                title='Proportion of canceled rentals superior to 12 hours time delta with previous rental',
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )    
    st.plotly_chart(fig)

    # Piechart proporion for delta ratio canceled cars with only <12 hours rentals
    fig = px.pie(data_ratio_delta_canceled,
                values='counts',
                names='delta',
                color = 'delta',
                width= 1000,
                title='Proportion of canceled rentals with time delta < 12 hours',
                color_discrete_sequence=px.colors.sequential.RdBu
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark',
                      legend=dict(yanchor= "bottom",y = -0.5, xanchor="right", x=0.5, orientation = "h")
                      )    
    st.plotly_chart(fig)
    st.write('Only 7% of canceled rentals are <12 hours of time delta with previous rentals')
    st.write('50% of <12 hours canceled rentals are for 0, 60, 600, 120 and 210 minutes time delta with previous rental')

    # Piechart proporion for checkin type influence on cancelation
    fig = px.pie(data_canceled_ratio_chekin,
                values='counts',
                names='checkin', 
                width= 1000,
                title='Proportion of Mobile and Connect Rentals for cancelation'
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )    
    st.plotly_chart(fig)
    st.write('60% of cancelation is for connect cars. Probably because it is easier to cancel a rental without an appointment with owner')

    # Piechart proporion for lateness influence on cancelation
    fig = px.pie(data_canceled_ratio_lateness,
                values='counts',
                names='lateness', 
                width= 1000,
                title='Proportion of in time & late previous rentals for canceled rentals',
                color_discrete_map={'late':'purple',
                                    'in time':'lightblue'}
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )    
    st.plotly_chart(fig)
    st.write('The lateness seems to have no influence in cancelation')

    st.subheader('3 | Set a treshold to display rentals')

    # Display delay at checkout in minutes distribution
    fig = px.histogram(data_canceled_late, x="delay_at_checkout_in_minutes_x",
                      title = 'Number of late rentals resulting in cancelation',
                      nbins= 250
                      ) 
    fig.update_layout(title_x = 0.5,
                      width = 1000,
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark',
                      yaxis_title = '',
                      xaxis_title = 'Delay at checkout'
                      )  
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                      'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )                       
    fig.add_vline(x = treshold_delay,
                  line_color = 'lightgreen',
                  annotation_text= 'Treshold'
                  )              
    st.plotly_chart(fig)
    st.write(f'The chosen treshold is {treshold_delay} minutes. It stop 80% of cancelation by lateness')

    st.subheader('4 | Impact of the chosen treshold on owners')
    st.write(f'There are {Rentals_affected} rentals affected by the treshold')
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )  
    st.plotly_chart(fig)
    st.write(f'For a minimum delay of {round(treshold_delay)} minutes between chechout & checkin the share of owners rentals is {round(owners_rentals_loss)} % lost')

def report():
    st.subheader('Which share of our owner’s revenue would potentially be affected by the feature ?')
    st.write('> 48 % of owners revenue will be lost if we set a treshold at 158 minutes')
    st.subheader('How many rentals would be affected by the feature depending on the threshold and scope we choose?')
    st.write('> With a 158 minutes treshold half of the rentals will be lost')
    st.write('> The scope does not affect the number of lost rentals')
    st.subheader('How often are drivers late for the next check-in? How does it impact the next driver?')
    st.write('> 57.5% of rentals are late to the checkout')
    st.write('> The lateness represent 46% of cancelation')
    st.subheader('How many problematic cases will it solve depending on the chosen threshold and scope?')
    st.write('> 80 % of cancelation are delete if we define a delay (treshold) at 158 minutes before display a car on the app')
    st.write('> The checkin type does not affect much the cancelation, 60% connect | 40% mobile')

if __name__ == "__main__":
    main()