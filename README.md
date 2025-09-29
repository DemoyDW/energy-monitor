# Energy Monitor     

## Problem Statement

Energy – how we create, store, and use it – is a topic that is of wide public interest. People have a financial interest (they pay for it), an ethical interest (how we generate power has huge impacts on climate change), and an interest based purely in curiosity.

While data on energy generation/usage in the UK is widely available, it’s also inaccessible and fragmented, with each of several different organisations managing different aspects and sharing their own datasets.


## Elevator Pitch 

A pipeline that tracks energy generation/costs, providing users with a single location to find a clear, understandable overview of power usage in the UK.

## Data Sources 

Elexon Insights APIs (data on price and generation, updated at 5-30 minute intervals)
The Carbon Intensity Forecast
The National Grid ESO data portal
The data feeds of various network operators, including information on current power outages (probably some scraping required here)
Octopus Energy API

## Proposed Solution & Functionality

The project will require several distinct elements:

  An extraction process that regularly gathers the latest data (given complexity of sources, this may actually end up being several processes running at slightly different frequencies – e.g. every 5 minutes for pricing from the API, but scraping power outages ~hourly)
  
  A database to store the collected data
  
  A dashboard to allow users to conduct interactive analysis
  
  A reporting process that produces summaries/alerts

## Planned outputs

An interactive dashboard that allows users to track & analyse power generation (e.g. by source), carbon intensity, and price both in near real-time and historically

Regular summary reports for subscribed users on power generation/price/carbon

Subscribable alerts for power outages in specific postcode regions.

## Tools & Technology Stack

Python (requests, Pandas, Psycopg2)
SQL
AWS (RDS, ECS, SNS/SES)

## Stretch Goals

Compare live pricing to existing tariffs offered by providers, so that users can see how much money they are saving/spending and which deals are best