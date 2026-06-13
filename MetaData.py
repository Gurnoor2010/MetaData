import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

def run_privacy_shield():
 
    root = tk.Tk()
    root.withdraw()

    print("️             --- MetaData --- ️")
    print("Select a target image using the file browser popup...\n")


    selected_file = filedialog.askopenfilename(
        title="Choose an Image to Clean", 
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp")]
    )

    if not selected_file:
        print(" Operation cancelled. No file was selected.")
        return

    print(f" Target File Locked: {selected_file}")

    try:
        with Image.open(selected_file) as img:
            img.load() 
            
            raw_exif = img.getexif() if hasattr(img, 'getexif') else None
            png_info = img.info if hasattr(img, 'info') else {}

            if (raw_exif and len(raw_exif) > 0) or (png_info and len(png_info) > 0):
     
                top_metrics = {
                    "Make": "Unknown", "Model": "Unknown", "Software": "Unknown",
                    "DateTime": "Unknown", "GPSInfo": " No GPS Track Found",
                    "ImageWidth": str(img.width), "ImageLength": str(img.height)
                }
                lower_metrics = {}

                for key, value in png_info.items():
                    if key in ["exif", "icc_profile"]: 
                        continue
                    if key in ["Creation Time", "date:create", "date:modify"]:
                        top_metrics["DateTime"] = str(value)
                    elif key in ["Software", "Description", "Author", "Copyright"]:
                        lower_metrics[f"PNG:{key}"] = str(value)

                if raw_exif:
                    for tag_id, value in raw_exif.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        
                        if tag_name in ["DateTimeOriginal", "DateTimeDigitized"]:
                            continue

                        if tag_name == "DateTime" and top_metrics["DateTime"] == "Unknown":
                            try:
                                dt_obj = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                                top_metrics["DateTime"] = dt_obj.strftime("%A, %d %B %Y at %I:%M %p")
                            except:
                                top_metrics["DateTime"] = str(value)

                        elif tag_name == "GPSInfo" and isinstance(value, dict):
                            try:
                                lat_ref = value.get(1, "N")
                                lat_data = value.get(2)
                                lon_ref = value.get(3, "E")
                                lon_data = value.get(4)
                                
                                if lat_data and lon_data:
                                    lat_deg = float(lat_data[0]) + (float(lat_data[1]) / 60.0) + (float(lat_data[2]) / 3600.0)
                                    lon_deg = float(lon_data[0]) + (float(lon_data[1]) / 60.0) + (float(lon_data[2]) / 3600.0)
                                    
                                    if lat_ref == "S": lat_deg = -lat_deg
                                    if lon_ref == "W": lon_deg = -lon_deg
                                    
                                    top_metrics["GPSInfo"] = f"{lat_deg:.6f}, {lon_deg:.6f}"
                            except:
                                top_metrics["GPSInfo"] = " Unparseable / Hidden Location Block"

                        elif tag_name in ["Make", "Model", "Software"]:
                            top_metrics[tag_name] = str(value)
                        else:
                            lower_metrics[tag_name] = str(value)

            print("\n [HIGH-PRIORITY IDENTITY LEAKS]")
            print("=" * 78)
            print(f"🔹 {'Device Manufacturer':<22} | {top_metrics['Make']}")
            print(f"🔹 {'Device Model':<22} | {top_metrics['Model']}")
            print(f"🔹 {'Operating Software':<22} | {top_metrics['Software']}")
            print(f"🔹 {'Date & Time':<22} | {top_metrics['DateTime']}")
            print(f"🔹 {'Geolocation':<22} | {top_metrics['GPSInfo']}")
            print(f"🔹 {'Image Dimensions':<22} | {top_metrics['ImageWidth']} x {top_metrics['ImageLength']} pixels")
            print("=" * 78)

            print("\n [SECONDARY HARDWARE METRICS]")
            print("-" * 78)
            for tag_name, value in lower_metrics.items():
                print(f"🔹 {str(tag_name):<22} | {value}")
  
            print("\n" + "="*78)
            strip_choice = input("️ Wiping Protocol Ready. Generate an anonymous copy? (y/n): ").lower()
            
            if strip_choice == 'y':
                dir_name = os.path.dirname(selected_file)
                base_name = os.path.basename(selected_file)
                name, ext = os.path.splitext(base_name)
                clean_file_path = os.path.join(dir_name, f"{name}_ANONYMOUS{ext}")
     
                pixel_colors = list(img.getdata())
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(pixel_colors)
                clean_img.save(clean_file_path)
                
                print(f"\n Privacy Shield Successful! All hidden tracking signatures purged.")
                print(f" Sterile file exported to: {name}_ANONYMOUS{ext}")
            else:
                print("\n Execution terminated. Target file header left unmodified.")
                            
    except Exception as e:
        print(f"\n Execution Interrupted: {e}")

if __name__ == "__main__":
    run_privacy_shield()
