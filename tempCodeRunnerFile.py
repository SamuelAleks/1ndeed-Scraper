    # HiringMultipleCandidatesModel
    hiring_multiple_candidates = job['hiringMultipleCandidatesModel']
    if hiring_multiple_candidates:
        hires_needed = hiring_multiple_candidates.get('hiresNeeded', '')
        hires_needed_exact = hiring_multiple_candidates.get('hiresNeededExact', '')
        sql_hiring = "INSERT INTO HiringMultipleCandidatesModel (jobkey, hiresNeeded, hiresNeededExact) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE hiresNeeded = VALUES(hiresNeeded), hiresNeededExact = VALUES(hiresNeededExact)"
        values_hiring = (jobkey, hires_needed, hires_needed_exact)
        mycursor.execute(sql_hiring, values_hiring)

    # RemoteWorkModel
    remote_work = job['remoteWorkModel']
    if remote_work:
        inline_text = remote_work.get('inlineText', False)
        text = remote_work.get('text', '')
        r_type = remote_work.get('type', '')
        sql_remote = "INSERT INTO RemoteWorkModel (jobkey, inlineText, text, type) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE inlineText = VALUES(inlineText), text = VALUES(text), type = VALUES(type)"
        values_remote = (jobkey, inline_text, text, r_type)
        mycursor.execute(sql_remote, values_remote)

    # SalarySnippet
    salary_snippet = job['salarySnippet']
    if salary_snippet:
        currency = salary_snippet.get('currency', '')
        salary_text_formatted = salary_snippet.get('salaryTextFormatted', False)
        source = salary_snippet.get('source', '')
        salary_text = salary_snippet.get('text', '')
        sql_salary = "INSERT INTO SalarySnippet (jobkey, currency, salaryTextFormatted, source, text) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE currency = VALUES(currency), salaryTextFormatted = VALUES(salaryTextFormatted), source = VALUES(source), text = VALUES(text)"
        values_salary = (jobkey, currency, salary_text_formatted, source, salary_text)
        mycursor.execute(sql_salary, values_salary)

    # TaxonomyAttributes
    taxonomy_attributes = job['taxonomyAttributes']
    for attribute in taxonomy_attributes:
        attribute_label = attribute.get('attributeLabel', '')
        attribute_value = attribute.get('attributeValue', '')
        sql_taxonomy = "INSERT INTO TaxonomyAttributes (jobkey, attributeLabel, attributeValue) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE attributeLabel = VALUES(attributeLabel), attributeValue = VALUES(attributeValue)"
        values_taxonomy = (jobkey, attribute_label, attribute_value)
        mycursor.execute(sql_taxonomy, values_taxonomy)
