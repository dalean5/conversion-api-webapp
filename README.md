# Simple File Conversion API

Hello friends 👋🏾, this repository contains sample code for a really simple file conversion api application. The code does the following:

- Accepts a CSV file and an email address
- Convert the CSV file to JSON
- Upload the JSON file to Azure storage
- Notify the user via an email that the file is ready

This pattern is very common where you have an application that should complete a sequence of tasks in a very specific order. We will compare this implementation to its Azure Durable Functions counterpart. [Please see the Azure Durable Functions implementation](https://github.com/dalean5/conversion-api-webapp).