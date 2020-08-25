# Covid-19 Simulation using Dash

Demo deployed at https://data-rnd-218011.appspot.com/

### Application in action:
![Covid Simulation Dash App Demo](demo.gif)

### Setup

Create a python virtual environment and run `pip install -r requirements.txt`

### Notes:
- This simulation is based on the analysis done in this article: [Link](https://medium.com/@tomaspueyo/coronavirus-act-today-or-people-will-die-f4d3d9cd99ca).
- It is known that there is a lag time before an infection gets reported as a confirmed case. So, a simulation model based on total number of deaths at present, fatality rate, days from infection to death, and case doubling rate has been used to estimate the actual true cases at present day.
- Number of cases that caused the deaths = Total deaths as of today / (Fatality rate (in %) / 100)
- Number of times cases have doubled = Days from infection to death / Case doubling time
- True cases today = Number of cases that caused the deaths * 2^(Number of times cases have doubled)
- True cases on Nth day from today = True cases today * 2^(Nth day number / Number of times cases have doubled)
- The default values of fatality rate, days from infection to death, and case doubling rate are sensible defaults determined by studies on actual data (more details in the article linked above), but feel free to tweak these values as well.
- Number of cases requiring hospitalizations, ICUs, ventilators have been adjusted by subtracting number of new cases from 10 days prior to account for cases that leave the hospital either due to recovery or death.
- Note that this is a very simple model that makes a lot of assumptions. Also, this model only shows the outbreak scenarios without accounting for containment, mitigation or other phases of intervention. Hence, the graphs only show infinitely increasing trends. However, this simulation (especially for N<=30 days) gives you an idea about how and when your hospital capacities might be pushed to their limits.
