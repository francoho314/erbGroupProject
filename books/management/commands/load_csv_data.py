import csv
import os
from django.core.management.base import BaseCommand
from books.models import Author, Genre, Book
from django.utils.dateparse import parse_date

class Command(BaseCommand):
    help = 'Load data from CSV files'
    
    def handle(self, *args, **options):
        # Load genres
        with open('genres.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Genre.objects.get_or_create(
                    GenreID=row['GenreID'],
                    defaults={'GenreName': row['GenreName']}
                )
        
        # Load authors
        with open('authors.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Author.objects.get_or_create(
                    AuthorID=row['AuthorID'],
                    defaults={
                        'FirstName': row['FirstName'],
                        'LastName': row['LastName'],
                        'Bio': row['Bio'],
                        'DateOfBirth': parse_date(row['DateOfBirth']),
                        'DateOfDeath': parse_date(row['DateOfDeath']) if row['DateOfDeath'] else None
                    }
                )
        
        # Load books
        with open('books.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    author = Author.objects.get(AuthorID=row['AuthorID'])
                    genre = Genre.objects.get(GenreID=row['GenreID'])
                    
                    Book.objects.get_or_create(
                        BookID=row['BookID'],
                        defaults={
                            'Title': row['Title'],
                            'AuthorID': author,
                            'GenreID': genre,
                            'ISBN': row['ISBN'],
                            'PublicationDate': parse_date(row['PublicationDate']),
                            'Price': row['Price'],
                            'Stock': row['Stock']
                        }
                    )
                except (Author.DoesNotExist, Genre.DoesNotExist) as e:
                    self.stdout.write(self.style.WARNING(f"Skipping book {row['BookID']}: {e}"))
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded CSV data'))