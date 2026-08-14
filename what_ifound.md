### **OKS**
1. It is a data manager that can read the configureation of the data acquistion system. DAQ have the many hardware and software system. At a time you need to specify to send data where to where and what type of data to collect. The OKS is liek the SDN control panel which sends the command(analogy like routing command as sent by the router) to the DAQ and also read the config. 
2. Why is it used? It is used beacuse rather than querying the database it queries the RAM directly of the multiple system thus it is so fast and thus was made to meed the demand.
3. IT has OKS API. Like we use a c libarary to access the files. We can use it using the C++, python or java. OKS provides API in these languages to interact with the OKS kernel system. So i do not know if the **BRJ sir** is correct or not about python needing the translation layer to C++.
4. In OKS query we are not using the standard SQL query rather we are using the object ids etc since it is the RAM query.

**What we need to do for the time being**
1. We need to make the separate DAQ mock but it should be as low priority. It shodld be the multiple systems and be able to take commands and send configuration as we have done but we need more research on the simplest of the true strcuture of the DAQ. What we have now is definetly not enough?. 
2. Then understand the OKS system or the kernel if we can clone from the sir given repo or what can we do. I am working on that.


