import pandas as pd
import random
import numpy as np

# read the publication data
authorship = pd.read_csv('work_authorship.csv')
# read the preprocessed institution data
inst_completeness =  pd.read_csv('inst_completeness.csv')

def group_info(author_i,df,backward_window,scientific_age_window):
    auship = df
    
    # Method1
    # mentor's all publications
    # works_i = auship['work_id'][auship.author_id==author_i]
    # print('len(works_i) : ',len(works_i))
    
    # Method2
    #mentor's all last-author publications
    works_i = auship['work_id'][(auship.author_id==author_i)&(auship.author_position=='last')]
    

    auship_i = auship[auship.work_id.isin(works_i)].sort_values(by='publication_year')
    # print('len(auship_i) : ',len(auship_i))

    auship_null = auship_i[~auship_i.institution_id.isnull()]

    # print('the ratio of with institution : ','{:.0%}'.format(len(auship_null)/len(auship_i)))
    
    years_i = auship_i.publication_year
    try:
        start_year = min(years_i)
        end_year = max(years_i)
    except:
        start_year = 2021
        end_year = 2022
    # print('start_year : ',start_year)
    # print('end_year : ',end_year)
    
    Group = pd.DataFrame([],columns=['work_id','author_position', 'author_id', 'institution_id', 'publication_year',
                                               'first_pub_year', 'scientific_age', 'group_size', 'mentor_id', 'current_year',         'ratio_institution','current_scientific_age'])
   
    for current_year in range(start_year,end_year+1):
        # print('current_year : ',current_year)
        auship_i_back = auship_i[(auship_i.publication_year>=current_year-backward_window)&
                                (auship_i.publication_year<=current_year)]
        auship_i_back_notnull = auship_i_back[~auship_i_back.institution_id.isnull()]
        
        
        auship_i_back =  auship_i_back.reset_index().drop(columns=['index'])
        #new consideration : current_scientific_age
        csa = np.array(auship_i_back['first_pub_year'] - current_year)*-1
        auship_i_back.loc[:,'current_scientific_age']  = csa
        
        
        if len(auship_i_back)==0:
            ratio_institution = 0
        else:
            ratio_institution = len(auship_i_back_notnull)/len(auship_i_back)
            
            # print('the ratio of with institution : ','{:.0%}'.format(ratio_institution))
        
        
        # ratio_institution = len(auship_i_back_notnull)/len(auship_i_back)
        # print('the ratio of with institution : ','{:.0%}'.format(ratio_institution))

        if not ratio_institution==0:
            try:
                institution_i = auship_i_back['institution_id'][auship_i_back.author_id==author_i].mode().iloc[0]
                # print('institution_i : ',institution_i)

                group_i = auship_i_back[(auship_i_back.institution_id==institution_i)
                                       &(auship_i_back.current_scientific_age<=scientific_age_window) # see above: current_scientific_age
                                       &(auship_i_back.author_id!=author_i)]

                group_size = len(set(group_i.author_id))
            # print('group_size : ',group_size)
            except:
                group_size = 0
            if group_size>0:
                group_i = group_i.assign(group_size = group_size)
                group_i = group_i.assign(mentor_id = author_i)
                group_i = group_i.assign(current_year = current_year)
                group_i = group_i.assign(ratio_institution = ratio_institution)
            else:
                group_i = pd.DataFrame([],columns=['work_id','author_position', 'author_id', 'institution_id', 'publication_year',
                                               'first_pub_year', 'scientific_age', 'group_size', 'mentor_id', 'current_year', 'ratio_institution','current_scientific_age'])
        else:
            group_i = pd.DataFrame([],columns=['work_id','author_position', 'author_id', 'institution_id', 'publication_year',
                                               'first_pub_year', 'scientific_age', 'group_size', 'mentor_id', 'current_year', 'ratio_institution','current_scientific_age'])
        Group = pd.concat((Group,group_i))
        
    return Group
