import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import tkinter as tk
from tkinter import messagebox, Scrollbar, StringVar, OptionMenu,simpledialog
import os
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
print(user_movie_matrix.head())
min_support = 0.4
frequent_itemsets = apriori(user_movie_matrix, min_support=min_support, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
print(rules.head())
# Film türleri ve başlıkları için liste oluşturma
all_genres = movies['genres'].str.split('|').explode().unique().tolist()
all_titles = movies['title'].tolist()

# Temel pencereyi oluştur
root = tk.Tk()
root.title("Film Öneri Sistemi")
root.geometry("400x400")
root.configure(bg="#2c3e50")
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

''# Kullanıcının tercih ettiği türleri seçmesi için pencere
def open_genre_preferences():
    preferences_window = tk.Toplevel(root)
    preferences_window.title("Favori Film Türlerinizi Seçin")

    # Kullanıcının seçebileceği türler için bir liste oluştur
    genre_vars = {genre: tk.BooleanVar() for genre in all_genres}

    # Türler için checkbox'lar ekle
    for genre in all_genres:
        checkbox = tk.Checkbutton(preferences_window, text=genre, variable=genre_vars[genre])
        checkbox.pack(anchor=tk.W)

    '''# Seçimlerin alınacağı buton
    select_button = tk.Button(preferences_window, text="Seçim Yap", command=lambda: on_genre_preferences_selected(genre_vars, preferences_window))
    select_button.pack(pady=10)'''

'''def on_genre_preferences_selected(genre_vars, window):
    selected_genres = [genre for genre, var in genre_vars.items() if var.get()]
    if selected_genres:
        recommend_movies_by_selected_genres(selected_genres)
    else:
        messagebox.showwarning("Uyarı", "Lütfen en az bir tür seçin!")
    window.destroy()'''

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


# Seçilen film türlerini gösteren pencere
def show_movie_genres(movie_title):
    movie = movies[movies['title'] == movie_title]
    if not movie.empty:
        genres = movie['genres'].values[0]  # Filmin türlerini al
        messagebox.showinfo("Film Türleri", f"{movie_title} türleri: {genres}")

# Öneri alanını güncelle
'''def show_recommendations(recommendations):
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
    listbox.bind("<Double-Button-1>", lambda event: show_movie_genres(listbox.get(listbox.curselection())))'''

'''def recommend_movies_by_selected_genres(selected_genres):
    recommendations = movies[movies['genres'].str.contains('|'.join(selected_genres))]
    recommendations_list = recommendations[['title', 'genres']].head(10)  # En iyi 10 öneriyi al

    if not recommendations_list.empty:
        show_recommendations(recommendations_list['title'].tolist())
    else:
        messagebox.showinfo("No Recommendations", "Seçtiğiniz türlere uygun film bulunamadı.")'''

# En iyi 50 filmi türüne göre önerme
def recommend_top_50_movies_by_genre(selected_genre):
    # Ortalama puan ve izlenme sayısını hesapla
    top_movies = ratings.groupby('movieId').agg({'rating': 'mean', 'userId': 'count'}).reset_index()
    top_movies.columns = ['movieId', 'average_rating', 'view_count']
    
    # En az 500 izlenme kaydı olan ve en yüksek puana sahip filmleri al
    top_movies = top_movies[top_movies['view_count'] >= 5000]
    
    # Seçilen türe göre film bilgilerini al
    genre_movies = top_movies.merge(movies[['movieId', 'title', 'genres']], on='movieId')
    genre_movies = genre_movies[genre_movies['genres'].str.contains(selected_genre, case=False)]

    # Liste oluşturma
    top_movies_list = []
    if not genre_movies.empty:
        top_movies_list.append(f"{selected_genre} Türündeki En İyi 50 Film:")
        for index, row in genre_movies.nlargest(50, 'average_rating').iterrows():
            top_movies_list.append(f"  - {row['title']} - Puan: {row['average_rating']:.1f} - İzlenme: {row['view_count']}")
    else:
        top_movies_list.append("Bu türde yeterli film bulunamadı.")

    show_recommendations(top_movies_list)

# Tür seçim penceresi
def open_genre_selection_for_top_movies():
    genre_selection_window = tk.Toplevel(root)
    genre_selection_window.title("Film Türü Seçin")

    genre_var = StringVar(genre_selection_window)
    genre_var.set(all_genres[0])  # İlk türü varsayılan olarak seç

    genre_menu = OptionMenu(genre_selection_window, genre_var, *all_genres)
    genre_menu.pack(pady=20)

    select_button = tk.Button(genre_selection_window, text="Seç", command=lambda: recommend_top_50_movies_by_genre(genre_var.get()))
    select_button.pack(pady=10)

# En iyi 50 film butonunu ekle
top_movies_button = tk.Button(root, text="En İyi 50 Filmi Göster", command=open_genre_selection_for_top_movies)
top_movies_button.pack(pady=10)

# Kullanıcı beğenileri için bir dosya adı
preferences_file = 'user_preferences.csv'

# Kullanıcı beğenilerini yükleme
def load_user_preferences():
    if os.path.exists(preferences_file):
        df = pd.read_csv(preferences_file)
        return {row['Username']: row['Preferences'].split(',') for _, row in df.iterrows()}
    return {}

# Kullanıcı beğenilerini kaydetme
def save_user_preferences():
    data = []
    for username, preferences in user_preferences.items():
        data.append({'Username': username, 'Preferences': ','.join(preferences)})
    df = pd.DataFrame(data)
    df.to_csv(preferences_file, index=False)

# Kullanıcı beğenileri için bir sözlük
user_preferences = load_user_preferences()

# Kullanıcı adı girişi
def enter_username():
    username = simpledialog.askstring("Kullanıcı Adı", "Lütfen adınızı girin:")
    if username:
        if username not in user_preferences:
            user_preferences[username] = []  # Yeni kullanıcı için boş bir liste oluştur
        select_movies(username)

def select_movies(username):
    movies_window = tk.Toplevel(root)
    movies_window.title(f"{username} için Filmleri Seçin")

    # Film listesi oluştur
    listbox = tk.Listbox(movies_window, selectmode=tk.MULTIPLE)
    for title in movies['title']:
        listbox.insert(tk.END, title)
    listbox.pack(pady=20)

    # Beğenilen filmleri kaydetmek için buton
    save_button = tk.Button(movies_window, text="Beğenilen Filmleri Kaydet", command=lambda: save_preferences(username, listbox))
    save_button.pack(pady=10)

def save_preferences(username, listbox):
    selected_indices = listbox.curselection()
    selected_movies = [listbox.get(i) for i in selected_indices]
    user_preferences[username].extend(selected_movies)  # Beğenilen filmleri ekle
    save_user_preferences()  # Beğenileri kaydet
    messagebox.showinfo("Bilgi", "Beğenilen filmler kaydedildi!")

    # Kullanıcı beğenilerini göster
    show_user_preferences(username)

def show_user_preferences(username):
    recommendations = user_preferences[username]
    if recommendations:
        show_recommendations(recommendations)
    else:
        messagebox.showinfo("Bilgi", "Henüz beğenilen film yok.")

# Kullanıcıların beğendiği filmleri gösterme
def show_all_preferences():
    all_preferences_window = tk.Toplevel(root)
    all_preferences_window.title("Kullanıcıların Beğendikleri Filmler")

    scrollbar = Scrollbar(all_preferences_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(all_preferences_window, yscrollcommand=scrollbar.set, width=50, height=20)

    for user, preferences in user_preferences.items():
        if preferences:
            listbox.insert(tk.END, f"{user}: {', '.join(preferences)}")
        else:
            listbox.insert(tk.END, f"{user}: Hiç beğenilen film yok.")

    listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar.config(command=listbox.yview)

# Temel pencereyi oluştur
root = tk.Tk()
root.title("Film Öneri Sistemi")
root.geometry("400x400")
root.configure(bg="#2c3e50")  # Koyu yeşil arka plan

# Kullanıcı girişi butonu
user_button = tk.Button(root, text="Kullanıcı Girişi", command=enter_username)
user_button.pack(pady=10)

# Tüm kullanıcıların beğendiği filmleri gösterme butonu
show_preferences_button = tk.Button(root, text="Kullanıcıların Beğendikleri Filmleri Göster", command=show_all_preferences)
show_preferences_button.pack(pady=10)

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
    
root.mainloop()

