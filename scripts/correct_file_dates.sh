for f in *.jpg; do
  echo "Processing $f";
  created_date_from_exif=$(mdls -raw -n kMDItemContentCreationDate "$f") # Pulls creation date from image's exif data
  formated_created_date=$(date -f '%F %T %z' -j "$created_date_from_exif" '+%D %T %z') # Converts creation date to a format that can be used by the date command
  SetFile -d "$formated_created_date" "$f" # Sets the file's creation date to the date pulled from the exif data
  SetFile -m "$formated_created_date" "$f" # Sets the file's modification date to the date pulled from the exif data
done
