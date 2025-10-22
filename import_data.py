import pandas as pd
import os
import django
import sys
from datetime import datetime
from decimal import Decimal

# Setup Django environment
sys.path.append('/Dropbox/erb/bookstore')  # Adjust this path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()

from books.models import Author, Genre, Book

def clean_isbn(isbn):
    """Clean and validate ISBN"""
    if pd.isna(isbn):
        return None
    isbn = str(isbn).strip().replace('-', '').replace(' ', '')
    if len(isbn) not in [10, 13]:
        return None
    return isbn

def clean_date(date_str):
    """Clean and parse date strings"""
    if pd.isna(date_str):
        return None
    try:
        # Try multiple date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y', '%Y-%m', '%d/%m/%Y']:
            try:
                return datetime.strptime(str(date_str).strip(), fmt).date()
            except ValueError:
                continue
        return None
    except:
        return None

def clean_price(price):
    """Clean and convert price to Decimal"""
    if pd.isna(price):
        return Decimal('0.00')
    try:
        if isinstance(price, str):
            price = price.replace('$', '').replace(',', '').strip()
        return Decimal(str(price))
    except:
        return Decimal('0.00')

def clean_stock(stock):
    """Clean stock quantity"""
    if pd.isna(stock):
        return 0
    try:
        stock_int = int(float(stock))
        return max(0, stock_int)
    except:
        return 0

def import_authors_and_genres_from_books(df):
    """Extract unique authors and genres from books data"""
    authors_created = 0
    genres_created = 0
    
    # Extract unique authors
    author_names = set()
    for _, row in df.iterrows():
        if 'authors' in df.columns and not pd.isna(row['authors']):
            authors = str(row['authors']).split(',')
            for author in authors:
                author_name = author.strip()
                if author_name and author_name not in author_names:
                    author_names.add(author_name)
    
    # Create author records
    author_mapping = {}
    for i, author_name in enumerate(author_names, 1):
        if author_name:
            # Split name into first and last name (simple approach)
            name_parts = author_name.split()
            first_name = name_parts[0] if name_parts else 'Unknown'
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'Author'
            
            author, created = Author.objects.get_or_create(
                FirstName=first_name[:100],
                LastName=last_name[:100],
                defaults={
                    'Bio': f"Author of multiple books",
                    'DateOfBirth': None
                }
            )
            author_mapping[author_name] = author
            if created:
                authors_created += 1
    
    # Extract unique genres
    genre_names = set()
    for _, row in df.iterrows():
        if 'categories' in df.columns and not pd.isna(row['categories']):
            genres = str(row['categories']).split(',')
            for genre in genres:
                genre_name = genre.strip()
                if genre_name and genre_name not in genre_names:
                    genre_names.add(genre_name)
    
    # Create genre records
    genre_mapping = {}
    for genre_name in genre_names:
        if genre_name:
            genre, created = Genre.objects.get_or_create(
                GenreName=genre_name[:100]
            )
            genre_mapping[genre_name] = genre
            if created:
                genres_created += 1
    
    print(f"Created {authors_created} new authors")
    print(f"Created {genres_created} new genres")
    
    return author_mapping, genre_mapping

def import_books(df, author_mapping, genre_mapping):
    """Import books data"""
    books_created = 0
    books_skipped = 0
    
    for index, row in df.iterrows():
        try:
            # Skip if essential data is missing
            if pd.isna(row.get('title')) or pd.isna(row.get('authors')):
                books_skipped += 1
                continue
            
            title = str(row['title']).strip()[:200]
            if not title:
                books_skipped += 1
                continue
            
            # Get author (use first author if multiple)
            authors_str = str(row['authors']).strip()
            first_author = authors_str.split(',')[0].strip()
            author = author_mapping.get(first_author)
            
            if not author:
                books_skipped += 1
                continue
            
            # Get genre (use first genre if multiple)
            genre = None
            if 'categories' in df.columns and not pd.isna(row['categories']):
                categories_str = str(row['categories']).strip()
                first_category = categories_str.split(',')[0].strip()
                genre = genre_mapping.get(first_category)
            
            # If no genre found, create or get a default one
            if not genre:
                genre, _ = Genre.objects.get_or_create(GenreName="General")
            
            # Clean other fields
            isbn = clean_isbn(row.get('isbn', row.get('isbn13', '')))
            publication_date = clean_date(row.get('publication_date', row.get('published_date', '')))
            price = clean_price(row.get('price', row.get('average_rating', 9.99)))
            stock = clean_stock(row.get('stock', row.get('ratings_count', 10)))
            
            # Handle thumbnail/image
            photo = ''
            if 'thumbnail' in df.columns and not pd.isna(row['thumbnail']):
                photo = str(row['thumbnail'])[:200]
            
            # Create book
            book, created = Book.objects.get_or_create(
                ISBN=isbn if isbn else f"TEMP_{index}",
                defaults={
                    'Title': title,
                    'AuthorID': author,
                    'GenreID': genre,
                    'PublicationDate': publication_date or datetime.now().date(),
                    'Price': price,
                    'Stock': stock,
                    'Photo': photo
                }
            )
            
            if created:
                books_created += 1
                
            if index % 100 == 0:
                print(f"Processed {index} books...")
                
        except Exception as e:
            print(f"Error importing book at index {index}: {str(e)}")
            books_skipped += 1
            continue
    
    print(f"Successfully created {books_created} books")
    print(f"Skipped {books_skipped} books due to errors or missing data")
    return books_created

def main():
    # Load the dataset
    file_path = 'books0.csv'
    
    try:
        print("Loading dataset...")
        df = pd.read_csv(file_path)
        print(f"Dataset loaded with {len(df)} rows and {len(df.columns)} columns")
        print("Columns:", df.columns.tolist())
        
        # Import authors and genres first
        print("\nImporting authors and genres...")
        author_mapping, genre_mapping = import_authors_and_genres_from_books(df)
        
        # Import books
        print("\nImporting books...")
        books_created = import_books(df, author_mapping, genre_mapping)
        
        print(f"\nImport completed successfully!")
        print(f"Total authors in database: {Author.objects.count()}")
        print(f"Total genres in database: {Genre.objects.count()}")
        print(f"Total books in database: {Book.objects.count()}")
        
    except Exception as e:
        print(f"Error during import: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()