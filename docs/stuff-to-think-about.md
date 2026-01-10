
* When to dry and when not to dry? drying early can restrict freedom later on.
    * i'm using the registry pattern to register each etl function. each etl is run like runEtl("table_name", config). this function uses a map to find the corresponding etl function. 
    * with ipcApi funcitons i'm also using a map 
* when to abstract/make stuff generic?
* should i use orm for electron backend?
* there are some data transformation done on frontend to get the clean data into the format the visuals require. would it better to ofload this to backend?
