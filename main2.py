import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import tkinter as tk
from tkinter import messagebox, Scrollbar, StringVar, OptionMenu

# Veri yükleme
movies = pd.read_csv('data/movies.csv')
ratings = pd.read_csv('data/ratings.csv')

# Kullanıcı-movie matrisi oluşturma
def create_user_movie_matrix():
    limited_users = ratings['userId'].value_counts().index[:10]
    limited_movies = ratings['movieId'].value_counts().index[:10]
    
    filtered_ratings = ratings[ratings['userId'].isin(limited_users) & ratings['movieId'].isin(limited_movies)]
    user_movie_matrix = filtered_ratings.pivot(index='userId', columns='movieId', values='rating')
    user_movie_matrix = (user_movie_matrix.notna()).astype(int).astype(bool)
    return user_movie_matrix

user_movie_matrix = create_user_movie_matrix()
min_support = 0.4
frequent_itemsets = apriori(user_movie_matrix, min_support=min_support, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

# Film türleri ve başlıkları için liste oluşturma
all_genres = movies['genres'].str.split('|').explode().unique().tolist()
all_titles = movies['title'].tolist()

# Temel pencereyi oluştur
root = tk.Tk()
root.title("Film Öneri Sistemi")
root.geometry("600x600")
root.configure(bg="#2c3e50")  # Koyu yeşil arka plan

# Öneri alanı
def show_recommendations(recommendations):
    recommendations_window = tk.Toplevel(root)
    recommendations_window.title("Öneriler")
    
    scrollbar = Scrollbar(recommendations_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(recommendations_window, yscrollcommand=scrollbar.set, width=50, height=20)
    for item in recommendations:
        listbox.insert(tk.END, item)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    
    scrollbar.config(command=listbox.yview)

# Popüler film önerileri
def recommend_popular_movies():
    # Top 50 izlenme sayısına göre film almak
    popular_movies = ratings.groupby('movieId').size().nlargest(50).reset_index(name='view_count')
    
    # Film bilgilerini ve puanlarını almak için birleştirme
    popular_movies = popular_movies.merge(movies[['movieId', 'title']], on='movieId')
    
    # İzlenme sayıları ile birlikte liste oluşturma
    popular_with_ratings = []
    for index, row in popular_movies.iterrows():
        movie_id = row['movieId']
        average_rating = ratings[ratings['movieId'] == movie_id]['rating'].mean()
        popular_with_ratings.append(f"{row['title']} - İzlenme: {row['view_count']} - Puan: {average_rating:.1f}")

    show_recommendations(popular_with_ratings)

# Film türüne göre öneri
def recommend_by_genre(genre):
    if genre:
        genre_movies = movies[movies['genres'].str.contains(genre, case=False)]
        if not genre_movies.empty:
            recommendations = genre_movies['title'].tolist()
            show_recommendations(recommendations)
        else:
            messagebox.showwarning("Uyarı", "Bu türde film bulunamadı!")

# Film ismine göre aynı türde öneri
def recommend_by_title(title):
    if title:
        movie = movies[movies['title'] == title]
        if not movie.empty:
            # Girdi film türünü al
            genres = movie['genres'].values[0].split('|')
            recommendations = movies[movies['genres'].str.contains('|'.join(genres)) & (movies['title'] != title)]
            recommendations_list = recommendations['title'].tolist()
            if recommendations_list:
                show_recommendations(recommendations_list)
            else:
                messagebox.showwarning("Uyarı", "Bu türde başka film bulunamadı!")
        else:
            messagebox.showwarning("Uyarı", "Film bulunamadı!")

# Kişiselleştirilmiş film önerisi
def recommend_personalized_movies(selected_movies):
    # Seçilen filmlerin türlerini al
    selected_genres = movies[movies['title'].isin(selected_movies)]['genres'].tolist()
    selected_genres_flat = [genre for sublist in selected_genres for genre in sublist.split('|')]

    # Türlere göre popüler filmleri bul
    genre_counts = pd.Series(selected_genres_flat).value_counts()
    top_genres = genre_counts.index[:3]  # En popüler 3 türü al

    recommended_movies = pd.DataFrame()

    for genre in top_genres:
        genre_movies = movies[movies['genres'].str.contains(genre)]
        recommended_movies = recommended_movies.append(genre_movies)

    # Tekrar eden filmleri kaldır ve öneri listesi oluştur
    recommended_movies = recommended_movies.drop_duplicates(subset=['movieId'])
    recommendations = recommended_movies[['title', 'genres']].head(10)  # En iyi 10 öneriyi al

    # Önerileri göster
    if not recommendations.empty:
        show_recommendations(recommendations['title'].tolist())
    else:
        messagebox.showinfo("No Recommendations", "No movies found for the selected genres.")



# Tür seçme penceresi
def open_genre_selection():
    genre_selection_window = tk.Toplevel(root)
    genre_selection_window.title("Film Türü Seçin")

    genre_var = StringVar(genre_selection_window)
    genre_var.set(all_genres[0])  # İlk türü varsayılan olarak seç

    genre_menu = OptionMenu(genre_selection_window, genre_var, *all_genres)
    genre_menu.pack(pady=20)

    select_button = tk.Button(genre_selection_window, text="Seç", command=lambda: on_genre_selected(genre_var.get(), genre_selection_window))
    select_button.pack(pady=10)

def on_genre_selected(genre, window):
    recommend_by_genre(genre)
    window.destroy()

# Film ismine göre öneri için pencere
def open_title_selection():
    title_selection_window = tk.Toplevel(root)
    title_selection_window.title("Film Seçin")

    title_var = StringVar(title_selection_window)
    title_var.set(all_titles[0])  # İlk filmi varsayılan olarak seç

    title_menu = OptionMenu(title_selection_window, title_var, *all_titles)
    title_menu.pack(pady=20)

    select_button = tk.Button(title_selection_window, text="Seç", command=lambda: on_title_selected(title_var.get(), title_selection_window))
    select_button.pack(pady=10)

def on_title_selected(title, window):
    recommend_by_title(title)
    window.destroy()

# Öneri türünü seçme
def recommend_based_on_selection():
    selection = recommendation_var.get()
    if selection == "Popüler Film Önerileri":
        recommend_popular_movies()
    elif selection == "Film Türüne Göre Öneri":
        open_genre_selection()  # Tür seçimi penceresini aç
    elif selection == "Film İsmine Göre Öneri":
        open_title_selection()  # Film ismi seçimi penceresini aç
    
    else:
        messagebox.showwarning("Uyarı", "Lütfen bir öneri türü seçin!")

# Popüler filmleri göstermek için buton
popular_movies_button = tk.Button(root, text="Popüler Filmleri Göster", command=recommend_popular_movies)
popular_movies_button.pack(pady=10)

# Öneri türleri için seçim alanı
recommendation_var = StringVar(root)
recommendation_var.set("Popüler Film Önerileri")  # Varsayılan seçenek

# Butonlar
genre_button = tk.Button(root, text="Film Türüne Göre Öneri", command=open_genre_selection)
genre_button.pack(pady=10)

title_button = tk.Button(root, text="Film İsmine Göre Öneri", command=open_title_selection)
title_button.pack(pady=10)

# Kullanıcının tercih ettiği türleri seçmesi için pencere
def open_genre_preferences():
    preferences_window = tk.Toplevel(root)
    preferences_window.title("Favori Film Türlerinizi Seçin")

    # Kullanıcının seçebileceği türler için bir liste oluştur
    genre_vars = {genre: tk.BooleanVar() for genre in all_genres}

    # Türler için checkbox'lar ekle
    for genre in all_genres:
        checkbox = tk.Checkbutton(preferences_window, text=genre, variable=genre_vars[genre])
        checkbox.pack(anchor=tk.W)

    # Seçimlerin alınacağı buton
    select_button = tk.Button(preferences_window, text="Seçim Yap", command=lambda: on_genre_preferences_selected(genre_vars, preferences_window))
    select_button.pack(pady=10)

def on_genre_preferences_selected(genre_vars, window):
    selected_genres = [genre for genre, var in genre_vars.items() if var.get()]
    if selected_genres:
        recommend_movies_by_selected_genres(selected_genres)
    else:
        messagebox.showwarning("Uyarı", "Lütfen en az bir tür seçin!")
    window.destroy()

# Seçilen türlere göre film önerisi
def recommend_movies_by_selected_genres(selected_genres):
    # Seçilen türlere göre film önerisi yap
    recommendations = movies[movies['genres'].str.contains('|'.join(selected_genres))]
    recommendations_list = recommendations[['title', 'genres']].head(10)  # En iyi 10 öneriyi al

    # Önerileri göster
    if not recommendations_list.empty:
        show_recommendations(recommendations_list['title'].tolist())
    else:
        messagebox.showinfo("No Recommendations", "Seçtiğiniz türlere uygun film bulunamadı.")

# Ana pencereden bu fonksiyonu çağırmak için bir buton ekleyin
preferences_button = tk.Button(root, text="Favori Türleri Seç", command=open_genre_preferences)
preferences_button.pack(pady=10)
# Seçilen film türlerini gösteren pencere
def show_movie_genres(movie_title):
    movie = movies[movies['title'] == movie_title]
    if not movie.empty:
        genres = movie['genres'].values[0]  # Filmin türlerini al
        messagebox.showinfo("Film Türleri", f"{movie_title} türleri: {genres}")

# Öneri alanını güncelle
def show_recommendations(recommendations):
    recommendations_window = tk.Toplevel(root)
    recommendations_window.title("Öneriler")
    
    scrollbar = Scrollbar(recommendations_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(recommendations_window, yscrollcommand=scrollbar.set, width=50, height=20)

    for item in recommendations:
        listbox.insert(tk.END, item)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    
    scrollbar.config(command=listbox.yview)

    # Listbox'a çift tıklama olayı ekle
    listbox.bind("<Double-Button-1>", lambda event: show_movie_genres(listbox.get(listbox.curselection())))

# Seçilen türlere göre film önerisi yapma
def recommend_movies_by_selected_genres(selected_genres):
    recommendations = movies[movies['genres'].str.contains('|'.join(selected_genres))]
    recommendations_list = recommendations[['title', 'genres']].head(10)  # En iyi 10 öneriyi al

    if not recommendations_list.empty:
        show_recommendations(recommendations_list['title'].tolist())
    else:
        messagebox.showinfo("No Recommendations", "Seçtiğiniz türlere uygun film bulunamadı.")




# Öneri butonu
recommend_button = tk.Button(root, text="Öneri Al", command=recommend_based_on_selection)
recommend_button.pack()


root.mainloop()
