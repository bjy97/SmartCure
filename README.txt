README - SmartCure

Jingya Bi, Shawn Shangzhou Xia

1. PostgreSQL account: sx2182
2. URL of our app: http://35.190.154.141:8111/ (This one does not work now)
3. Description: SmartCure is an application that aims at making wise recommendations to patients in search of economical in-patient health service providers nearby based on a large-scale database with previous diagnoses and treatment information. 
We implemented the entire original design in part 1, where we envisioned the application to make recommendations to users seeking in-patient health services based on their own information. We also implemented a brand new feature that takes the total cost into consideration when making the recommendations. In this final application, the user is prompted to enter his/her zip code, select from broad categories of diseases, and select a price range that s/he anticipates. The user is also asked to select his/her most concern from doctor specialization, location and estimated costs. After we sort out all doctor-and-hospital tuples satisfying all the conditions, we provide the user with a form with results order by his/her concern.

4. Examples:
Zip code = 100, Symptom = 'Digestive System', Expected cost = 0-10000, Most concern = 'Location'.
Zip code = 120, Symptom = 'Digestive System', Expected cost = 0-10000, Most concern = 'cost'.

The first example shows how we sort the results first according to the distance between the hospital and the user, and then according to the average cost by previous patients staying in that hospital. The second on is implemented by order of average cost.

5.Limitations:
a.The app now only asks for the first three digits of the user’s zip code because in-patient records we have only disclose first three digits of patients’ zip code. In order to make recommendations more suitable for users, we would like to have more precise user address information by asking users either to input their five digit zip codes, or to pin on the map where they are. 
b.Among the three most concerns, price range mandates users to have all three fields filled (symptom, zip code, price range) based on the current sql query we have. However, users may only want to disclose one or two out of the three fields we provide, so we need to have different queries for each situation. 
