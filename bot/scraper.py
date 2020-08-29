#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import requests
from bs4 import BeautifulSoup


# In[2]:


def weworkremotely_jobs():
    r = requests.get("https://weworkremotely.com/")
    page = BeautifulSoup(r.text, "html.parser")
    job_section = page.find("section", {"id": "category-2"})

    jobs = []
    for job in job_section.find_all("li", {"class": "feature"}):
        jobs.append({
            "href": "https://weworkremotely.com" + job.find_all("a")[1]["href"],
            "company": job.find("span", {"class": "company"}).text.strip(),
            "role": job.find("span", {"class": "title"}).text.strip(),
            "job_type": job.find_all("span", {"class": "company"})[1].text.strip(),
            "location": job.find("span", {"class": "region company"}).text.strip()
        })
    return jobs


# In[3]:


def weworkremotely_info(href):
    r = requests.get(href)
    page = BeautifulSoup(r.text, "html.parser")

    title = page.find(
        "div", {"class": "listing-header-container"}).find("h1").text.strip()
    tags = [i.text.strip().lower()
            for i in page.find_all("span", {"class": "listing-tag"})]
    description = page.find(
        "div", {"id": "job-listing-show-container"}).text.strip()
    return {
        "title": title,
        "tags": tags,
        "description": description,
        "href": href
    }


# In[4]:


def remoteok_jobs():
    r = requests.get("https://remoteok.io/remote-dev-jobs")
    page = BeautifulSoup(r.text, "html.parser")

    first_index = str(page).find("<thead>")
    second_index = str(page)[first_index + 7:].find("<thead>")
    job_section = BeautifulSoup(
        str(page)[first_index:second_index], "html.parser")

    jobs = []
    for job in job_section.find_all("tr", {"class": "job"}):
        try:
            job_info = json.loads(str(job.find("script"))[35:-9])
            jobs.append({
                "href": "https://remoteok.io" + job["data-url"],
                "company": job_info["hiringOrganization"]["name"],
                "role": job_info["title"],
                "job_type": job_info["employmentType"],
                "location": job_info["jobLocation"]["address"]["addressCountry"],
                "description": job_info["description"],
                "tags": [i.text.strip().lower() for i in job.find("td", {"class": "tags"}).find_all("h3")]
            })
        except:
            pass
    return jobs


# In[5]:


def employremotely_jobs():
    r = requests.get("https://www.employremotely.com/jobs")
    page = BeautifulSoup(r.text, "html.parser")

    jobs = []
    for job in page.find_all("div", {"class": "c-job-card"}):
        jobs.append({
            "href": "https://www.employremotely.com" + job.find("span", {"class": "c-job-card__job-title"}).find("a")["href"],
            "company": job.find("span", {"class": "c-job-card__company"}).text.strip(),
            "role": job.find("span", {"class": "c-job-card__job-title"}).find("a").text.strip(),
            "job_type": job.find("span", {"class": "c-job-card__contract-type"}).text.strip()[2:],
            "location": job.find("span", {"class": "c-job-card__location"}).text.strip()[2:]
        })
    return jobs


# In[6]:


def employremotely_info(href):
    r = requests.get(href)
    page = BeautifulSoup(r.text, "html.parser")

    title = page.find("h1", {"class": "u-c--white"}).text.strip()
    deadline = page.find_all(
        "span", {"class": "job-header__detail"})[-1].text.strip()
    tags = [i.text.strip().lower() for i in page.find("section", {
        "class": "job-information__tags"}).find_all("span", {"class": "c-pill"})]
    description = page.find(
        "section", {"class": "job-information__text-block"}).text.strip()
    return {
        "title": title,
        "tags": tags,
        "deadline": deadline[2:],
        "description": description,
        "href": href
    }


# In[7]:


def remotive_jobs():
    r = requests.get("https://remotive.io/remote-jobs/software-dev")
    page = BeautifulSoup(r.text, "html.parser")
    job_section = page.find("ul", {"class": "job-list"})

    jobs = []
    for job in job_section.find_all("li"):
        if job.find("span", {"class": "job-date--old"}):
            continue
        try:
            location = job.find("span", {"class": "location"}).text.strip()
        except:
            location = ""
        jobs.append({
            "href": "https://remotive.io" + job["data-url"],
            "company": job.find("div", {"class": "company"}).find("span").text.strip(),
            "role": job.find("a").text.strip(),
            "location": location,
            "tags": [i.text.strip().lower() for i in job.find_all("a", {"class": "job-tag"})]
        })
    return jobs


# In[8]:


def remotive_info(href):
    r = requests.get(href)
    page = BeautifulSoup(r.text, "html.parser")

    company = page.find("div", {"class": "content"}).find("h2").text.strip()
    title = page.find("div", {"class": "content"}).find("h1").text.strip()
    tags = [i.text.strip().lower() for i in page.find(
        "div", {"class": "job-tags"}).find_all("a", {"class": "job-tag"})]
    description = page.find("div", {"class": "job-description"}).text.strip()
    return {
        "company": company,
        "title": title,
        "tags": tags,
        "description": description
    }


# In[9]:


def stackoverflow_jobs():
    r = requests.get("https://stackoverflow.com/jobs")
    page = BeautifulSoup(r.text, "html.parser")
    job_section = page.find("div", {"class": "listResults"})

    jobs = []
    for job in job_section.find_all("div", {"class": "-job"}):
        jobs.append({
            "href": "https://stackoverflow.com" + job.find("a", {"class": "s-link"})["href"],
            "location": job.find("span", {"class": "fc-black-500"}).text.strip(),
            "company": job.find("h3", {"class": "fc-black-700"}).find("span").text.strip(),
            "role": job.find("a", {"class": "s-link"})["title"],
            "tags": [i.text.strip().lower() for i in job.find_all("a", {"class": "post-tag"})]
        })
    return jobs


# In[10]:


def stackoverflow_info(href):
    r = requests.get(href)
    page = BeautifulSoup(r.text, "html.parser")

    title = page.find("h1", {"class": "fs-headline1 mb4"}).text.strip()
    company = page.find("a", {"class": "fc-black-700"}).text.strip()
    tags = [i.text.strip().lower() for i in page.find_all("section", {"class": "mb32"})[
        1].find_all("a", {"class": "post-tag no-tag-menu"})]
    description = page.find("div", {"id": "overview-items"}).text.strip()
    return {
        "title": title,
        "company": company,
        "tags": tags,
        "description": description
    }


# In[11]:


def github_jobs():
    job_section = requests.get("https://jobs.github.com/positions.json").json()

    jobs = []
    for job in job_section:
        jobs.append({
            "href": job["url"],
            "location": job["location"],
            "title": job["title"],
            "company": job["company"],
            "job_type": job["type"],
            "description": job["description"]
        })
    return jobs


# In[ ]:
