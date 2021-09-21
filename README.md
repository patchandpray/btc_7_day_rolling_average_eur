# Calculate BTC 7 day rolling average in EUR

This application fetches the bitcoin price index data in USD and generates the last day rolling average in EUR for the last year using the reference exchange rate from the European Central Bank.

This application outputs this data in CSV format.

This application outputs a visualisation of the 7-day average over time as pdf.

## How to run

The source directory utilises `make` targets for setup, testing and running the application:

To run the application from source directory use `make run`

To test the application from source directory use `make test`

Other `make` targets are provided, please see the enclosed `Makefile`.

## How to deploy to production with daily run

### CI/CD

A CI/CD pipeline would control the release of the application to Production.
The pipeline will take care of automated testing, verification and release of the code with at least the following steps on Test:

- Check -> Can all dependencies for this application be resolved, are any prerequisites met
- Lint -> Does code adhere to our standards
- Test
  * Unit -> Testing the smallest possible components without dependency on external systems or other internal methods / functions
  * Integration -> Testing methods and functions in combination with other systems, services or methods / functions
  * E2E -> Black box testing where we measure the application run  as a whole by verifying output is as expected based on a set of predetermined inputs in the actual environment.
- Build -> Once verification steps have completed the application can be built. Depending on how we want to release and use this application (library, serverless function, on kubernetes) this step will determine the artifact that will be output. Release is tagged and versioned with release notes and can be reused in subsequent Release steps.
- Release -> Manual (release / review gate) or automated (CD) deployment of the build artifact to enviroment.

Once pipeline run has completed and application is live on Test environment ideally we would repeate the following steps for subsequent environments:
- Test
  - E2E
- Release

### Production

Application can be run as part of a workflow using a workflow management framework (Airflow / Argo for example) or called by an event or cron like scheduler depending on the environment.

Improvements for production use:
- Application metrics using statsd -> add where necessary.
- Monitoring and alerting.
- Data Quality tests as part of workflow 
- Identify and implement preferred way of storing and using application outputs (currently they are just output to disk)

Another consideration would be to further isolate parts of this applications functionality, parametrize them and enable them as re-useable components to be orchestrated by a worfklow management system. This will open up the components for more use-cases but should only be done when actual use-cases can be identified to not fall in the trap op premature optimisation and abstraction.


