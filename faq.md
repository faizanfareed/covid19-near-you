

## How COVID-19 NEAR YOU app can help to control transmission ? 

COVID-19 transmissions routes ( by WHO )

- **Symptomatic transmission  :**
    > "By way of definition, a symptomatic COVID-19 case is a case who has developed signs and
                            symptoms
                            compatible with COVID-19 virus infection. Symptomatic transmission refers to transmission
                            from a
                            person while they are experiencing symptoms. Data from published epidemiology and virologic
                            studies
                            provide evidence that COVID-19 is primarily transmitted from symptomatic people to others
                            who are in
                            close contact through respiratory droplets, by direct contact with infected persons, orby
                            contact with
                            contaminated objects and surfaces.1-7This is supported by detailed experiences shared by
                            technical
                            partners via WHO global expert networks, and reports and presentations by Ministries of
                            Health.Data
                            from clinical and virologic studies that have collected repeated biological samples from
                            confirmed patients provide evidence that shedding of the COVID-19 virus is highest in upper
                            respiratory tract (nose and throat) early in the course of the disease.8-11 That is, within
                            the first
                            3 days from onset of symptoms.10-11Preliminary data suggests that people may be more
                            contagious
                            around the time of symptom onset as compared to later on in the disease."

 - **Pre-symptomatic transmission :**
   > "The incubation period for COVID-19, which is the time between exposure to the virus
                            (becoming infected) and
                            symptom onset, is on average 5-6 days, however can be up to 14 days. During this period,
                            also known as the
                            “pre-symptomatic” period, some infected persons can be contagious. Therefore, transmission
                            from a
                            pre-symptomatic
                            case can occur before symptom onset."

- **Asymptomatic transmission :**
  > "An asymptomatic laboratory-confirmed case is a person infected with COVID-19 who does not
                            develop symptoms.
                            Asymptomatic transmission refers to transmission of the virus from a person, who does not
                            develop symptoms.
                            There are few reports of laboratory-confirmed cases who are truly asymptomatic,
                            and to date, there has been no documented asymptomatic transmission.
                            This does not exclude the possibility that it may occur. Asymptomatic cases
                            have been reported as part of contact tracing efforts in some countries.
                            WHO regularly monitors all emerging evidence about this critical topic and
                            will provide an upda te as more information becomes available."

When new COVID-19 confirmed case came from a specific region, higher probability other carriers which are Symptomatic , Pre-symptomatic and Asymptomatic transmitting the COVID-19.

We are using same COVID-19 incubation period for region which will be indicating if new cases coming from specific region (during region peroid time ) that's mean other carriers are existing in region and transmitting COVID-19. If no new casese coming from region (until the time expired of region ) that's mean no carriers in that region. 

Finds confirmed cases in 1,2 and 3 km and quarantine center in 10 Km radius range and give  advices based on user given position.

*    Find users zone if they are in Red, Yellow or Green zone based on confirmed case aorund them.
*    Give advices to people what they should do or not if they are in infected region or not.
*    Show cluster of COVID-19 regions for officals to take right decisions. And  for public  to take  appropriate precautions.Officials can
      * Easily identify infected regions, and then  impose lockdown and run awareness compaign.
      * (Local authorities) can take quick and real time decision. 
      * Identify those regions where no of cases increasing.
*    Show nearest confirmed case and Quarantine center point (address , distance (from user position) and radius range).      
*    Show  total no of confirmed cases  and no of points in different ranges  around user.
*    Provides WHO (World Health Organization) and  National  website links for latest information  and some other useful links  
       * [Myth busters]( https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters)
       * [When and how to use masks](https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/when-and-how-to-use-masks)
       * [Advice for public]( https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public)
       * [Advocacy](    https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/healthy-parenting)
* Users can also check other regions in case of if they wanna go or someone coming from infected regions based on result they will take appropriate precautions.
 

If people already knows about infected regions and people of these regions transmitting the virus,then they will avoid them, (infected regions and thier people as well) so they will be definitely taking necessary precautions.


**Using COVID-19 incubation peroid for region (points)  and  above all points will help to control COVID-19 transmission  .**



# COVID-19 app directives  

## What is 1, 2 and 3 km radius range?

App find points in different radius ranges which are 1, 2 and 3 km based on this alert users, shows how many points existed around them and giving appropriate precautions.
FIRST_RANGE_CIRCLE, SECOND_RANGE_CIRCLE ,THIRD_RANGE_CIRCLE and RANGE_IN_UNITS (RANGE_IN_UNITS used for range units in km,meter,miles) directives are used.


## What is Quarantine radius ?

If any Quarantine point near you in 10 km radius range it will show you.
QUARANTINE_RADIUS_RANGE and QUARANTINE_RADIUS_RANGE_UNIT directives are used.


## What is Map Center Point ?

Map center points are used to show which country you want to show on Map.
MAP_CENTER_POINT_LATITUDE and MAP_CENTER_POINT_MAGNITUDE directives are used.


## What is Country Boundry ?

Country bounrdy is basically bound the user location (latitude , longitude). Used for validations.
Change these according to your country bounrdy.Set Min,Max latitude and longitude. It is basically polygon.
REGION_BOUNDRY_MIN_LATITUDE, REGION_BOUNDRY_MAX_LATITUDE ,REGION_BOUNDRY_MIN_LONGITUDE and REGION_BOUNDRY_MAX_LONGITUDE directives are used.


## What is region incubation peroid time?

Region incubation peroid time is COVID-19 incubation peroid time for controling the transmission. See How COVID-19 NEAR YOU app can help to control transmission ?

 ## What is batch size ?

Find nearest point feature is using Redis database which is store data in-memory, if data lost we need to add data into Redis database in batches from MYSQL database.
LOCATION_CACHE_BATCH_SIZE directive is used.

## What is Geospatial File update time ?

All data points are saved into Geojson file to plot data on map. We need to add new points and delete old ones every 12/24 hours later.We set geospatial file update time which will be indicating when to update points. 
COVID19_UPDATE_DATA_TIME directive is used.


## What is website links and names ?

COVID-19 NEAR YOU application is open source project so any country can use this. If any country using this app MY_COUNTRY_COVID19_WEB_LINK_NAME and MY_COUNTRY_COVID19_WEB_LINK directives are for them to add own national health website link and name. And WHO_WEBSITE_LINK_NAME and WHO_WEBSITE_LINK directives are used for World Health Organization. 


## Country name ?

By default COUNTRY_NAME directive set to 'PAKISTAN'. If any country want to use this app they can change country name.