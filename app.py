import requests
import os
import sys
from dotenv import load_dotenv
# Menggunakan library rich untuk tampilan terminal yang lebih menarik
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich import box
except ImportError:
    print("Library 'rich' belum terinstall. Menginstall otomatis...")
    os.system('pip install rich')
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box

# Inisialisasi Rich Console
console = Console()

def main():
    # Load environment variables
    load_dotenv()
    
    # Ambil API KEY dari .env
    api_key = os.getenv("API_KEY")
    
    if not api_key:
        console.print("[bold red]Error:[/bold red] API_KEY tidak ditemukan di file .env!")
        return

    # Tampilan Header
    console.print(
        Panel.fit(
            "[bold cyan]Aplikasi Pantau Cuaca Real-Time[/bold cyan]\n[italic white]Powered by OpenWeatherMap[/italic white]",
            border_style="blue",
            box=box.DOUBLE
        )
    )

    # Input kota dari user
    city = console.input("[bold yellow]Masukkan nama kota:[/bold yellow] ").strip()
    
    if not city:
        console.print("[red]Nama kota tidak boleh kosong![/red]")
        return

    # Loading status
    with console.status(f"[bold green]Mengambil data untuk {city}...", spinner="dots"):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=id"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if response.status_code == 200:
                # Parsing data
                name = data.get("name")
                country = data.get("sys", {}).get("country")
                temp = data.get("main", {}).get("temp")
                feels_like = data.get("main", {}).get("feels_like")
                humidity = data.get("main", {}).get("humidity")
                desc = data.get("weather", [{}])[0].get("description")
                wind_speed = data.get("wind", {}).get("speed")

                # Membuat Tabel Output yang Keren
                table = Table(title=f"Informasi Cuaca: {name}, {country}", title_style="bold magenta", box=box.ROUNDED)
                
                table.add_column("Parameter", style="cyan", no_wrap=True)
                table.add_column("Keterangan", style="white")

                table.add_row("Suhu Saat Ini", f"{temp}°C")
                table.add_row("Terasa Seperti", f"{feels_like}°C")
                table.add_row("Kondisi", desc.capitalize())
                table.add_row("Kelembapan", f"{humidity}%")
                table.add_row("Kecepatan Angin", f"{wind_speed} m/s")

                console.print("\n", table)
                
                # Memberikan saran berdasarkan cuaca
                if "hujan" in desc.lower():
                    console.print("[bold yellow]Tips: Jangan lupa bawa payung ya! ☔[/bold yellow]")
                elif temp > 30:
                    console.print("[bold orange1]Tips: Cuaca cukup panas, tetap terhidrasi! 🥤[/bold orange1]")
                else:
                    console.print("[bold green]Tips: Cuaca cukup nyaman untuk beraktivitas. ✨[/bold green]")

            elif response.status_code == 404:
                console.print(f"\n[bold red]Error:[/bold red] Kota '{city}' tidak ditemukan. Cek kembali ejaannya.")
            else:
                console.print(f"\n[bold red]Error:[/bold red] Gagal mengambil data. (Status: {response.status_code})")

        except requests.exceptions.ConnectionError:
            console.print("\n[bold red]Error:[/bold red] Koneksi internet bermasalah.")
        except Exception as e:
            console.print(f"\n[bold red]Error Tidak Terduga:[/bold red] {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Program dihentikan oleh pengguna.[/yellow]")
        sys.exit()