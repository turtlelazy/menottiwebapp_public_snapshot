# Menotti Enterprise Flask App - Ishraq Mahid

## Purpose
This repository contains company software solutions and serves them through a Flask App. These solutions are the automatic billing Quickbooks integration and the construction safety guidelines consultation bot. The Flask app includes not only these services but also a user portal to restrict access to company tools to registered employees.

## Login
The website is password-protected and utilizes bcrypt hashing to further ensure the security of the website. 

## Automatic Quickbooks Billing
The automatic billing integration relies on pandas and calls to the Quickbooks API. When the user enters the weekly schedule, it's deconstructed using pandas and processed into a JSON payload. This JSON payload (after going through the Quickbooks authorization process) is used to create invoices for multiple locations using the Quickbooks API.

## Automatic Consultation
By utilizing OpenAI's GPT 3.5-turbo API, I utilize langchain and embed New York City's construction safety and guidelines code book. Using these embeddings, GPT can be prompted to answer questions regarding this code book. This way, rather than going through the code book manually, GPT can grab the necessary information and respond to a user's prompts. 

## Deployment
This repo is deployed to a DigitalOcean droplet for Menotti Enterprise, LLC, using Guinicorn.
