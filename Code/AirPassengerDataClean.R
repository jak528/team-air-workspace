air_traffic<-read.csv("AIRPA_Traffic.csv")
coach <- read.csv("CoachPA.csv")
park <- read.csv("PublicParking.csv")
shareDrive <- read.csv("SharedDrive.csv")
shareDrive_reservation <- read.csv("SharedDrive_Reservation.csv")
taxi <- read.csv("Taxi.csv")

colnames(air_traffic)[1] <- "Airport"
air_traffic$Month <- match(air_traffic$Month,month.abb)

total <- merge(coach,park,by=c("Airport","Year","Month"),all=TRUE)
total <- merge(total,shareDrive,by=c("Airport","Year","Month"),all=TRUE)
total <- merge(total,shareDrive_reservation,by=c("Airport","Year","Month"),all=TRUE)
total <- merge(total,taxi,by=c("Airport","Year","Month"),all=TRUE)

total$Airport = as.character(total$Airport)


total[grepl("Kennedy",total$Airport),]$Airport <- "JFK"
total[grepl("LaGuardia",total$Airport),]$Airport <- "LGA"
total[grepl("Liberty",total$Airport),]$Airport <- "EWR"

total <- merge(total,air_traffic,by=c("Airport","Year","Month"),all=TRUE)
