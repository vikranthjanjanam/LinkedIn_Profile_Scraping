#!/usr/bin/env python
# coding: utf-8

# In[1]:


## !pip install selenium


# In[2]:


## !pip install bs4


# In[3]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import time
from datetime import datetime

import pandas as pd


# In[4]:


def linkedin_connect(driver_path = "C:\\Users\\vikra\\Documents\\LinkedIn_GRA\\WebDrivers\\chromedriver.exe", username_value = "vikranthjanjanam@gmail.com", password_value = "!1Vikranth"):
    
    # Creating a webdriver instance
    driver = webdriver.Chrome(driver_path)
    driver.maximize_window()
    # This instance will be used to log into LinkedIn

    # Opening linkedIn's login page
    driver.get("https://linkedin.com/login")

    # waiting for the page to load
    time.sleep(5)

    # entering username
    username = driver.find_element("id", "username")

    # In case of an error, try changing the element
    # tag used here.

    # Enter Your Email Address
    username.send_keys(username_value)

    # entering password
    pword = driver.find_element("id", "password")
    # In case of an error, try changing the element
    # tag used here.

    # Enter Your Password
    pword.send_keys(password_value)    

    # Clicking on the log in button
    # Format (syntax) of writing XPath -->
    # //tagname[@attribute='value']
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    # In case of an error, try changing the
    # XPath used here.
    return driver


driver = linkedin_connect()


# In[5]:


def get_profile_source(driver):

    # this will open the link

    start = time.time()

    # will be used in the while loop
    initialScroll = 0
    finalScroll = 1000

    while True:
        driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
        # this command scrolls the window starting from
        # the pixel value stored in the initialScroll
        # variable to the pixel value stored at the
        # finalScroll variable
        initialScroll = finalScroll
        finalScroll += 1000

        # we will stop the script for 1 second so that
        # the data can load
        time.sleep(2)
        # You can change it as per your needs and internet speed

        end = time.time()

        # We will scroll for 10 seconds.
        # You can change it as per your needs and internet speed
        if round(end - start) > 15:
            break

    src = driver.page_source

    # Now using beautiful soup
    soup = BeautifulSoup(src, 'lxml')
    
    return soup


# In[6]:


def get_about(soup):
    
    try:
        # Extracting the HTML of the complete introduction box
        # that contains the name, company name, and the location
        about_data = soup.find('div', {'id': 'about'}).parent
        #print(exp_data)

        about_list = about_data.find_all('span', {'aria-hidden': 'true'})
        return about_list[1].get_text().strip()
    except Exception as e:
        return None
    finally:
        pass


# In[7]:


def get_intro(soup, profile_url):
    
    # Extracting the HTML of the complete introduction box
    # that contains the name, company name, and the location
    intro = soup.find('div', {'class': 'pv-text-details__left-panel'})
    #print(intro)
    
    # Extracting the Name
    first_name = None
    last_name = None
    try:
        name_loc = intro.find("h1")
        name = name_loc.get_text().strip()
        first_name = name.split()[0]
        last_name = ' '.join(name.split()[1:]).strip()
    except Exception as e:
        print(e)
    finally:
        pass
    # strip() is used to remove any extra blank spaces
    
    # Ectracting the Gender
    # The 2nd element in the gender
    gender = None
    try:
        gender_text = intro.find_all("span", {'class': 'text-body-small'})
        gender = gender_text[0].get_text().strip()
        
        if 'She' in gender:
            gender = 'Female'
        elif 'He' in gender:
            gender = 'Male'
        else:
            gender = None
    except Exception as e:
        print(e)
    finally:
        pass
    
    location = None
    try:
        loc_text = soup.find_all("span", {'class': 'text-body-small inline t-black--light break-words'})
        location = loc_text[0].get_text().strip()
    except Exception as e:
        print(e)
    finally:
        pass
    
    about = get_about(soup)
    
    intro = {
        "profile": profile_url,
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "location": location,
        "about": about
    }
    
    return [intro]
    
    


# In[8]:


def get_normal_experience(experience, exp_values, profile_url):
    
    title, company, work_type, from_date, till_date, duration, location, details = None, None, None, None, None, None, None, None
    details = ''
    
    for i in range(len(exp_values)):

        value = exp_values[i]
        #print("\n", value.get_text().strip(), value.parent, "\n\n")
        
        if value == None:
                continue

        if value.parent == experience.find('span', {'class': 'mr1 t-bold'}):
            title = value.get_text().strip()

        elif value.parent == experience.find('span', {'class': 't-14 t-normal'}):
            company = value.get_text().strip()

            try:
                comp_type = company.split(' · ')
                if len(comp_type) > 1:
                    work_type = comp_type[-1]
                    company = " ".join(comp_type[0:-1])
                else:
                    company = comp_type[0]
            except Exception as e:
                print(e, "Company")

        elif value.parent in experience.find_all('span', {'class': 't-14 t-normal t-black--light'}):

            value1 = value.get_text().strip()
            #print(value1)

            if (' - ' not in value1) and (' · ' not in value1):
                location = value1

            else:
                value = value1.split(' · ')
                duration = value[1]

                period = value[0]
                if ' - ' in period:
                    from_date = period.split(' - ')[0]
                    till_date = period.split(' - ')[1]

#                     if till_date.strip() == "Present":
#                         active = True
#                         till_date = None
#                     else:
#                         active = False
                else:
                    # active = False
                    from_date = till_date = period

        elif value.parent == experience.find('div', {'class': 'inline-show-more-text inline-show-more-text--is-collapsed'}):
            details += '\n' + value.get_text().strip()
        elif value.parent == experience.find('div', {'class': 'inline-show-more-text inline-show-more-text--is-collapsed inline-show-more-text--is-collapsed-with-line-clamp'}):
            details += '\n' + value.get_text().strip()
        elif value.parent == experience.find('div', {'class': 'display-flex align-items-center t-14 t-normal t-black'}):
            details += '\n' + value.get_text().strip()
        elif value.parent == experience.find('div', {'class': 'inline-show-more-text inline-show-more-text--is-collapsed inline-show-more-text--is-collapsed-with-line-clamp t-14 t-bold break-words'}):
            details += '\n' + value.get_text().strip()
            
    details = None if details == '' else details.strip()
    
    experience_details = {
        "profile": profile_url,
        "title": title,
        "company": company,
        "work_type": work_type,
        "from_date": from_date,
        "till_date": till_date,
        # "active": active,
        "duration": duration,
        "exp_location": location,
        "details": details
    }
    
    return [experience_details]


# In[9]:


def get_nested_experience(experience, exp_values, profile_url):
    
    ###### nolink
    ## company - span, mr1 hoverable-link-text t-bold
    ## Roles - span, mr1 hoverable-link-text t-bold
    ## Period, Loc - span, t-14 t-normal t-black--light
    ## Details - div, inline-show-more-text inline-show-more-text--is-collapsed
    
    ###### link
    ## company - span, mr1 hoverable-link-text t-bold
    ## Roles - span, mr1 hoverable-link-text t-bold
    ## Period, Loc - span, t-14 t-normal t-black--light
    ## Details - div, display-flex align-items-center t-14 t-normal t-black
    
    company = exp_values[0].get_text().strip()
    
    exp_list = experience.find_all('li', {'class': 'pvs-list__paged-list-item'})
    experience_details = []
    
    for exp in exp_list:
        
        exp_values = exp.find_all('span', {'aria-hidden': 'true'})
        
        title, work_type, from_date, till_date, duration, location, details = None, None, None, None, None, None, None
        details = ''

        for i in range(len(exp_values)):

            value = exp_values[i]
            #print("\n", value.get_text().strip(), value.parent, "\n\n")
            
            if value == None:
                continue

            if value.parent == exp.find('span', {'class': 'mr1 hoverable-link-text t-bold'}):
                title = value.get_text().strip()

            elif value.parent in exp.find_all('span', {'class': 't-14 t-normal t-black--light'}):

                value1 = value.get_text().strip()
                #print(value1)

                if (' - ' not in value1) and (' · ' not in value1):
                    location = value1

                else:
                    value = value1.split(' · ')
                    duration = value[1]

                    period = value[0]
                    if ' - ' in period:
                        from_date = period.split(' - ')[0]
                        till_date = period.split(' - ')[1]

#                         if till_date.strip() == "Present":
#                             active = True
#                             till_date = None
#                         else:
#                             active = False
                    else:
                        # active = False
                        from_date = till_date = period

            elif value.parent == exp.find('div', {'class': 'inline-show-more-text inline-show-more-text--is-collapsed'}):
                details += '\n' + value.get_text().strip()
            elif value.parent == exp.find('div', {'class': 'inline-show-more-text inline-show-more-text--is-collapsed inline-show-more-text--is-collapsed-with-line-clamp'}):
                details += '\n' + value.get_text().strip()
            elif value.parent == exp.find('div', {'class': 'display-flex align-items-center t-14 t-normal t-black'}):
                details += '\n' + value.get_text().strip()
            elif value.parent == exp.find('div', {'class': 'inline-show-more-text inline-show-more-text--is-collapsed inline-show-more-text--is-collapsed-with-line-clamp t-14 t-bold break-words'}):
                details += '\n' + value.get_text().strip()

        details = None if details == '' else details.strip()

        experience_detail = {
            "profile": profile_url,
            "title": title,
            "company": company,
            "work_type": work_type,
            "from_date": from_date,
            "till_date": till_date,
            # "active": active,
            "duration": duration,
            "exp_location": location,
            "details": details
        }
        experience_details += [experience_detail]
        
    return experience_details


# In[10]:


def get_experience(driver, soup, profile_url):
    
    exp_list = []
    try:
        # Extracting the HTML of the complete introduction box
        # that contains the name, company name, and the location
        exp_data = soup.find('div', {'id': 'experience'}).parent
        #print(exp_data)

        exps_links = exp_data.find_all('a', {'class': 'optional-action-target-wrapper artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--muted inline-flex justify-center full-width align-items-center artdeco-button--fluid'})
        many_exp = True if len(exps_links) > 0 else False
        # print(many_exp)

        if many_exp == True:

            exp_a_text = exps_links[0].get_text().strip()
            exp_link = driver.find_element("link text", exp_a_text)

            driver.execute_script("arguments[0].click();", exp_link)
            # @class='optional-action-target-wrapper artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--muted inline-flex justify-center full-width align-items-center artdeco-button--fluid'

            soup_exp = get_profile_source(driver)
            exp_data = soup_exp.find_all('div', {'class': "scaffold-finite-scroll__content"})[0]
            # print(exp_data)


            experiences = exp_data.find_all('li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})

            driver.back()

        else:
            experiences = exp_data.find_all('li', {'class': 'artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})


        exp_list = []
        for experience in experiences:
            
            if experience == None:
                continue

            exp_values = experience.find_all('span', {'aria-hidden': 'true'})
            # print("\n\n", exp_values, "\n\n")

            exp_type = "normal" if exp_values[0].parent == experience.find('span', {'class': 'mr1 t-bold'}) else "nested"
            # print(exp_type, exp_values[0].parent)

            if exp_type == "normal":
                exp_data = get_normal_experience(experience, exp_values, profile_url)
            else:
                exp_data = get_nested_experience(experience, exp_values, profile_url)

            exp_list += exp_data

    except Exception as e:
        print("No Experience found\n\n", e)
        return []
    finally:
        pass
    
    return exp_list


# In[11]:


def get_normal_education(education, edu_values, profile_url):
    
    school, degree, major, from_date, till_date = None, None, None, None, None
    
    for i in range(len(edu_values)):

        value = edu_values[i]
        
        if value == None:
                continue

        if value.parent == education.find('span', {'class': 'mr1 hoverable-link-text t-bold'}):
            school = value.get_text().strip()

        elif value.parent == education.find('span', {'class': 't-14 t-normal'}):
            degree = value.get_text().strip()

            try:
                degree_type = degree.split(", ")
                if len(degree_type) > 1:
                    major = degree_type[-1].strip()
                    degree = " ".join(degree_type[0:-1])
                else:
                    degree = degree_type[0]
            except Exception as e:
                print(e, "Degree")

        elif value.parent in education.find_all('span', {'class': 't-14 t-normal t-black--light'}):

            period = value.get_text().strip()
            # print(value1)

            if ' - ' in period:
                from_date = period.split(' - ')[0]
                till_date = period.split(' - ')[1]

                if till_date.strip() == "Present":
                    till_date = None
            
            else:
                from_date = till_date = period
    
    edu_details = {
        "profile": profile_url,
        "school": school,
        "degree": degree,
        "major": major,
        "from_date": from_date,
        "till_date": till_date
    }
    
    return [edu_details]


# In[12]:


def get_education(driver, soup, profile_url):
    
    exp_list = []
    try:
        # Extracting the HTML of the complete introduction box
        # that contains the name, company name, and the location
        edu_data = soup.find('div', {'id': 'education'}).parent
        # print(edu_data)

        edu_links = edu_data.find_all('a', {'class': 'optional-action-target-wrapper artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--muted inline-flex justify-center full-width align-items-center artdeco-button--fluid'})
        many_edu = True if len(edu_links) > 0 else False
        #print(many_exp)
        
        if many_edu == True:
            
            edu_a_text = edu_links[0].get_text().strip()
            edu_link = driver.find_element("link text", edu_a_text)
            
            driver.execute_script("arguments[0].click();", edu_link)
            # @class='optional-action-target-wrapper artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--muted inline-flex justify-center full-width align-items-center artdeco-button--fluid'
            
            soup_edu = get_profile_source(driver)
            edu_data = soup_edu.find_all('div', {'class': "scaffold-finite-scroll__content"})[0]
            #print(edu_data)
            
            
            academics = edu_data.find_all('li', {'class': 'pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated'})
            
            driver.back()
        
        else:
            academics = edu_data.find_all('li', {'class': 'artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})
        
        
        edu_list = []
        for education in academics:
            
            if education == None:
                continue
            
            edu_values = education.find_all('span', {'aria-hidden': 'true'})
            # print("\n\n", exp_values, "\n\n")
            
            edu_data = get_normal_education(education, edu_values, profile_url)
                
            edu_list += edu_data
            
    except Exception as e:
        print("No Education found\n\n", e)
        return []
    finally:
        pass
    
    return edu_list


# In[13]:


def scrape_linkedin_profile(driver, profile_url):
    
    driver.get(profile_url)
    source_soup = get_profile_source(driver)

    intro = get_intro(source_soup, profile_url)
    
    experience = get_experience(driver, source_soup, profile_url)
    
    education = get_education(driver, source_soup, profile_url)
    
    return {
        'intro': intro,
        'experience': experience,
        'education': education
    }


# In[14]:


def create_pd_df(data_list, category):
    
    df = pd.DataFrame(data_list)
    return df


# In[15]:


def save_category_df(df, category):
    
    out_path = "C:\\Users\\vikra\\Documents\\LinkedIn_GRA\\Data\\Results\\"
    file_path = out_path + category + '_' + str(datetime.today().strftime('%Y.%m.%d_%H.%M')) + ".csv"
    
    df.to_csv(file_path, header = True, index = False, sep = ',')


# In[17]:


def scrape_profiles_list(driver, profiles):
    
    intro_list = []
    exp_list = []
    edu_list = []
    
    start = time.time()
    for profile in profiles:

        p_start = time.time()
        data = scrape_linkedin_profile(driver, profile)
        p_end = time.time()
        print("\n%s Completed in: %.2f Seconds\n" % (profile, p_end - p_start))
        
        intro_list += data['intro']
        exp_list += data['experience']
        edu_list += data['education']
        
    end = time.time()
    print("\n\nTotal Time: %.2f Seconds" % (end - start))
    
    # print(intro_list[:5])
    # print(exp_list[:5])
    # print(edu_list[:5])
    
    intro_df = create_pd_df(intro_list, "intro")
    exp_df = create_pd_df(exp_list, "experience")
    edu_df = create_pd_df(edu_list, "education")
    
    profiles_data = {
        "intro_df": intro_df,
        "exp_df": exp_df,
        "edu_df": edu_df,
    }
    
    intro_df = profiles_data['intro_df']
    
    return profiles_data


# In[18]:


profiles = [
    "https://www.linkedin.com/in/elizabethweil",
    "https://www.linkedin.com/in/alexisohanian",
    "https://www.linkedin.com/in/davidjli",
    "https://www.linkedin.com/in/matt-holleran-291a773",
    "https://www.linkedin.com/in/reidchristian",
    
    "https://www.linkedin.com/in/heath-lukatch-86a2a",
    "https://www.linkedin.com/in/karahartnetthurst",
    "https://www.linkedin.com/in/jim-momtazee-65634918b",
    "https://www.linkedin.com/in/masaya-kawakami-581b6b6b",
    "https://www.linkedin.com/in/ryosukek",
    
    ## "https://www.linkedin.com/in/george-montgomery-3a4a2120",
    
    "https://www.linkedin.com/in/ravishankar-g-v-259423/",
    "https://www.linkedin.com/in/ando-masaaki-2832927b/",
    "https://www.linkedin.com/in/keisukewada",
    "https://www.linkedin.com/in/morgan-kessous-b3b94628",
    "https://www.linkedin.com/in/geeta-vemuri-24849b105",
    
    "https://www.linkedin.com/in/lawrence-handen-8376728",
    "https://www.linkedin.com/in/ravimhatre",
    "https://www.linkedin.com/in/yochai-hacohen-05b9423",
    "https://www.linkedin.com/in/petechung",
    "https://www.linkedin.com/in/sumir-chadha-bb8b563",
]

profiles_data = scrape_profiles_list(driver, profiles)


# In[21]:


def join_data(df1, df2):
    
    merged_df = df1[['profile', 'first_name', 'last_name', 'location']].merge(df2, on = 'profile')
    return merged_df


# In[22]:


def refine_data(profiles_data):
    
    intro_df = profiles_data['intro_df']
    exp_df = profiles_data['exp_df']
    edu_df = profiles_data['edu_df']
    
    exp_df = join_data(intro_df, exp_df)
    edu_df = join_data(intro_df, edu_df)
    
    profiles_data = {
        "intro_df": [intro_df],
        "exp_df": [exp_df],
        "edu_df": [edu_df],
    }
    
    save_category_df(intro_df, "intro")
    save_category_df(exp_df, "experience")
    save_category_df(edu_df, "education")
#     save_category_df(merged_df, "merged")
    
#     for key, value in profiles_data:
#         save_category_df(value[0], key.split('_')[0])
    
    return profiles_data


# In[23]:


joined = refine_data(profiles_data)


# In[ ]:





# In[ ]:




