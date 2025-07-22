# Libraries
import sqlite3
import csv
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu

# Part 1, Data Management
def import_cell_count_data(db_name: str, csv_file: str):
    with sqlite3.connect(db_name, timeout=10, check_same_thread=False) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;") # Enable foreign key constraints

        # Create tables
        cur.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT UNIQUE
        )
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT UNIQUE,
            age INTEGER,
            sex TEXT,
            treatment TEXT,
            response TEXT,
            project_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        ''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT UNIQUE,
            sample_type TEXT,
            time_from_treatment_start TEXT,
            b_cell INTEGER,
            cd8_t_cell INTEGER,
            cd4_t_cell INTEGER,
            nk_cell INTEGER,
            monocyte INTEGER,
            people_id INTEGER,
            FOREIGN KEY (people_id) REFERENCES people(id)
        )
        ''')

        # Read and import data
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                cur.execute('INSERT OR IGNORE INTO projects (project) VALUES (?)', (row['project'],))
                cur.execute('SELECT id FROM projects WHERE project = ?', (row['project'],))
                project_id = cur.fetchone()[0]

                cur.execute('''
                    INSERT OR IGNORE INTO people (subject, age, sex, treatment, response, project_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    row['subject'],
                    int(row['age']),
                    row['sex'],
                    row['treatment'],
                    row['response'],
                    project_id
                ))
                cur.execute('SELECT id FROM people WHERE subject = ?', (row['subject'],))
                people_id = cur.fetchone()[0]

                cur.execute('''
                INSERT OR REPLACE INTO samples (
                    sample_id, sample_type, time_from_treatment_start,
                    b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte, people_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['sample'],
                    row['sample_type'],
                    row['time_from_treatment_start'],
                    int(row['b_cell']),
                    int(row['cd8_t_cell']),
                    int(row['cd4_t_cell']),
                    int(row['nk_cell']),
                    int(row['monocyte']),
                    people_id
                ))

                if i % 1000 == 0:
                    conn.commit()
                    print(f"Committed {i} rows...")

            conn.commit()
        cur.close()

# Part 2
def generate_cell_frequency_summary(db_name: str):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    cell_types = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']

    cursor.execute(f'''
        SELECT sample_id, {", ".join(cell_types)}
        FROM samples
    ''')
    samples = cursor.fetchall()

    summary_data = []
    for row in samples:
        sample_id = row[0]
        counts = row[1:]
        total_count = sum(counts)

        for pop, count in zip(cell_types, counts):
            percentage = round((count / total_count) * 100, 2) if total_count else 0
            summary_data.append({
                'sample': sample_id,
                'total_count': total_count,
                'population': pop,
                'count': count,
                'percentage': percentage
            })

    cursor.close()
    connection.close()
    df_summary = pd.DataFrame(summary_data)
    return df_summary

# Part 3
def analyze_response_effects(df_summary: pd.DataFrame, db_name: str):
    conn = sqlite3.connect(db_name)

    # Add metadata to df_summary
    metadata = pd.read_sql_query('''
        SELECT s.sample_id, p.response, s.sample_type, p.treatment
        FROM samples s
        JOIN people p ON s.people_id = p.id
    ''', conn)

    merged = df_summary.merge(metadata, left_on='sample', right_on='sample_id')

    # Filter for melanoma PBMC samples treated with miraclib
    filtered = merged[(merged['sample_type'] == 'PBMC') & (merged['treatment'] == 'miraclib')]

    palette = {'yes': '#c5d6c7', 'no': '#e6e2ca'}
    fig, axes = plt.subplots(1, len(filtered['population'].unique()), figsize=(18, 5))
    sig_results = []
    
    for i, pop in enumerate(filtered['population'].unique()):
        data = filtered[filtered['population'] == pop]
        sns.boxplot(data=data, x='response', y='percentage', ax=axes[i], palette=palette)
        axes[i].set_title(pop)
        axes[i].set_ylabel("Relative Frequency (%)")
        axes[i].set_xlabel("")
        group1 = data[data['response'] == 'yes']['percentage']
        group2 = data[data['response'] == 'no']['percentage']
        if len(group1) > 0 and len(group2) > 0:
            stat, p = mannwhitneyu(group1, group2, alternative='two-sided')
            if p < 0.05:
                sig_results.append((pop, p))
    
    plt.tight_layout()
    return fig, sig_results

# Part 4
def melanoma_baseline_summary(db_name: str):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT pr.project, p.response, p.sex
        FROM samples s
        JOIN people p ON s.people_id = p.id
        JOIN projects pr ON p.project_id = pr.id
        WHERE s.sample_type = 'PBMC'
          AND s.time_from_treatment_start = '0'
          AND p.treatment = 'miraclib'
    ''')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['project', 'response', 'sex'])

    summary = {
        'samples_per_project': df['project'].value_counts().to_dict(),
        'responders': df['response'].value_counts().get('yes', 0),
        'non_responders': df['response'].value_counts().get('no', 0),
        'sex_distribution': df['sex'].value_counts().to_dict()
    }

    return summary
