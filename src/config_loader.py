"""Load job preferences from config file."""
import re

def load_job_preferences(config_file="config/job_preferences.md"):
    """Parse job_preferences.md and return structured config."""
    with open(config_file, 'r') as f:
        content = f.read()

    config = {
        'locations': [],
        'roles': [],
        'must_haves': [],
        'nice_to_haves': [],
        'experience': {},
        'skills': [],
        'salary_min': 60000,
    }

    # Extract Target Locations
    locations_match = re.search(r'## Target Locations\n(.*?)(?=\n##)', content, re.DOTALL)
    if locations_match:
        for line in locations_match.group(1).split('\n'):
            line = line.strip().lstrip('- ').strip()
            if line and not line.startswith('['):
                config['locations'].append(line)

    # Extract Target Roles
    roles_match = re.search(r'## Target Roles\n(.*?)(?=\n##)', content, re.DOTALL)
    if roles_match:
        for line in roles_match.group(1).split('\n'):
            line = line.strip().lstrip('- ').strip()
            if line and not line.startswith('['):
                config['roles'].append(line)

    # Extract Must-Haves
    must_haves_match = re.search(r'## Must-Haves.*?\n(.*?)(?=\n##)', content, re.DOTALL)
    if must_haves_match:
        for line in must_haves_match.group(1).split('\n'):
            line = line.strip().lstrip('- [ ] ').lstrip('- [x] ').strip()
            if line:
                config['must_haves'].append(line)

    # Extract Nice-to-Haves
    nice_match = re.search(r'## Nice-to-Haves.*?\n(.*?)(?=\n##)', content, re.DOTALL)
    if nice_match:
        for line in nice_match.group(1).split('\n'):
            line = line.strip().lstrip('- [ ] ').lstrip('- [x] ').strip()
            if line:
                config['nice_to_haves'].append(line)

    # Extract Experience Profile
    exp_match = re.search(r'## Experience Profile.*?\n(.*?)(?=\n##)', content, re.DOTALL)
    if exp_match:
        exp_text = exp_match.group(1)
        years_match = re.search(r'\*\*Years of experience\*\*:\s*([\d\-]+)', exp_text)
        if years_match:
            config['experience']['years'] = years_match.group(1)

        skills_match = re.search(r'\*\*Key skills\*\*:\s*(.+?)(?=\n\*\*)', exp_text)
        if skills_match:
            config['skills'] = [s.strip() for s in skills_match.group(1).split(',')]

        education_match = re.search(r'\*\*Education\*\*:\s*(.+?)(?=\n)', exp_text)
        if education_match:
            config['experience']['education'] = education_match.group(1)

    # Extract Salary
    salary_match = re.search(r'Salary\s*>=\s*€?([\d,]+)', content)
    if salary_match:
        config['salary_min'] = int(salary_match.group(1).replace(',', ''))

    # Extract Email Recipients
    email_match = re.search(r'Primary:\s*<(.+?)>', content)
    if email_match:
        config['email_recipient'] = email_match.group(1)

    # Extract Grading Thresholds
    strong_match = re.search(r'\*\*Strong match\*\*:\s*(\d+)-(\d+)/10', content)
    if strong_match:
        config['threshold_strong'] = int(strong_match.group(1))

    good_match = re.search(r'\*\*Good match\*\*:\s*(\d+)-(\d+)/10', content)
    if good_match:
        config['threshold_good'] = int(good_match.group(1))

    # CV options: which template, and whether to force a single page.
    template_match = re.search(r'(?im)^\s*[-*]?\s*Template:\s*(.+?)\s*$', content)
    config['template'] = template_match.group(1).strip() if template_match else 'single_column_article'

    one_page_match = re.search(r'(?im)^\s*[-*]?\s*One[\s-]?page:\s*(yes|no|true|false)\b', content)
    config['one_page'] = (one_page_match.group(1).lower() in ('yes', 'true')) if one_page_match else True

    return config

def get_user_profile(config):
    """Convert config to user profile for grading."""
    return {
        'years_experience': config['experience'].get('years', '2-5'),
        'skills': config['skills'],
        'location_pref': ', '.join(config['locations']),
        'salary_min': config['salary_min'],
        'education': config['experience'].get('education', 'CS degree'),
    }
