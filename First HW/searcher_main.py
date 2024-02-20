import requests
import os

# Список URL для скачивания
urls_file_path = 'urls.txt'
with open(urls_file_path, 'r') as file:
    urls = [line.strip() for line in file if line.strip()]

output_dir = "pages"
os.makedirs(output_dir, exist_ok=True)

index_file_path = os.path.join(output_dir, "index.txt")
with open(index_file_path, "w", encoding="utf-8") as index_file:
    for i, url in enumerate(urls, start=1):
        try:
            response = requests.get(url)
            response.raise_for_status()

            file_path = os.path.join(output_dir, f"page_{i}.html")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(response.text)

            index_file.write(f"{i}: {url}\n")

            print(f"Сохранено: {url}. Под названием: {file_path}")
        except requests.RequestException as e:
            print(f"{url}: {e}")

print("Загрузка завершена.")
