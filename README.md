# Travelling-Agency

A travelling agency which customizes trips for customers. A trip plan consists of a hotel reservation in a requested time interval and a flight reservation for requested number of travelers.

## Details

Using this agency, a customer informs the travel agency of the arrival and departure date of his trip, his preferred hotel, airline and the number of travelers. Then the travel agency contacts to the hotel and airline and ask for availability for the corresponding dates. If there are available rooms for the given number of people in the hotel and available seats in the flight for a given number of travelers, then the travel agency finalizes the trip.

![img](https://i.ibb.co/pn6Vd70/Customer-Single.jpg)

When the trip is finalized, the updates are reflected in the databases of the hotel and the airline. If the preferred hotel or airline is unavailable, then the databases remain unchanged and the travel agency contacts to alternative hotel(s) or airline(s) and propose an itinerary to the customer. If the customer accepts the proposed itinerary, then the travel agency can finalize the trip as before. Otherwise, the travel agency will keep on generating another itinerary until it runs out of options.

The customer uses TCP sockets to communicate with the travel agency. The travel agency communicates with the hotels and airlines using HTTP requests. The customer side is running on node.js server while the agency runs on a python server. Each hotel and airline has its own database to keep track of availability. The travel agency does not have a direct access to these databases.

![img](https://i.ibb.co/XD3tLG2/General-Structure.jpg)

Client-side is a simple GUI where the customer can enter the desired informations and send the request to the agency. The customer can accept or reject the alternative itinerary if proposed.

## Implementation

The customer-side is running on a web-browser. The front-end is written in HTML/CSS/JS and the back-end is written in node.js and express. The customer screen is shown above. To be able to test multiple customers, we wrote it in a different way. You can add infinite number of customers and send different requests to the agency.

The agency is running on a python server. The bigger portion of this project is the agency itself. Because it does multiple jobs at the same time. We can list these jobs as in here:

- Return the names of the hotels and airlines to the customer
- Get the request from the customer and process it
- Ask if there is enough place in the preferred hotel and airline
- If there is enough place, ask again to the hotel and airline for the reservation
- Return the successful answer back to the customer
- If there is not enough place, check other hotels and airlines that are registered in the hotels and airlines database
- If any place found, propose an itinerary to the customer
- If customer accepts the itinerary, ask to the hotel and airline for the reservation
- If the customer rejects the itinerary, check other hotels and airlines that are registered in the hotels and airlines database
- Register any new hotel and airline when they send a request when they get created

![img](https://i.ibb.co/4FVV3cW/Hotel-Creator.jpg)

Also there exists hotel and airline creator scripts. When you run them, it asks you a few questions like the name and port of the server. When it is created, it makes a request to the agency and the agency adds it to its own database to be able to access it later.
