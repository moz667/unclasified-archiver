#!/bin/bash

set -e

create_img() {
    local index=$1
    local bg_color=$2
    local creation_time=$3
    local output_file=$4

    echo " * Generando $output_file..."

    # Generar la imagen con ImageMagick y añadir el EXIF
    convert -size "320x240" xc:"$bg_color" -gravity center \
        -pointsize "100" -fill "black" -annotate +0+0 "$index" \
        "$output_file"
    
    if [ "$creation_time" != "" ]; then
        exiftool -q -m -overwrite_original "-datetimeoriginal=$creation_time" "$output_file"
    fi
}

create_vid() {
    local duration=$1
    local creation_time=$2
    local output_file=$3

    echo " * Generando $output_file..."

    ffmpeg -y -f lavfi -i testsrc=size=320x240:rate=1 -vf hue=s=0 -vcodec libx264 \
        -preset superfast -tune zerolatency -pix_fmt yuv420p -t $duration -movflags +faststart \
        -metadata creation_time="$creation_time" \
        $output_file > /dev/null 2>&1
}

exif_dates=(\
2024-09-01\ 08:00:00 \
2024-08-01\ 08:00:00 \
2024-07-01\ 08:00:00 \
2024-06-01\ 08:00:00 \
2024-05-01\ 08:00:00 \
2024-04-01\ 08:00:00 \
2024-03-01\ 08:00:00 \
2024-02-01\ 08:00:00 \
2024-01-01\ 08:00:00 \
2023-12-01\ 08:00:00)

DIR_SAMPLES=test-files/samples

if [ -d $DIR_SAMPLES ]; then
    echo "ERROR: Ya existe el directorio $DIR_SAMPLES"
    exit 2
fi

# Creamos el directorio $DIR_SAMPLES
mkdir -p $DIR_SAMPLES

# Archivos base (con diferentes exif dates y demas)
current_dir=$DIR_SAMPLES/01-base
mkdir -p $current_dir

for i in {1..10}; do
    creation_time=${exif_dates[$((i-1))]}
    duration=$i
    file_name_index=`printf "%02d" $i`
    
    create_vid $duration "$creation_time" "$current_dir/video-$file_name_index.mp4"

    img_creation_time=`echo ${exif_dates[$((i-1))]} | sed -e "s/-/:/g"`
    img_bg_arg=$((i-1))

    create_img $i "#FFFFF$img_bg_arg" "$img_creation_time" "$current_dir/image-$file_name_index.jpg"
done

# Archivos que colisionen con diferente checksum (con mismo nombre y mismo exif dates)
current_dir=$DIR_SAMPLES/02-base-diferent-checksum
mkdir -p $current_dir

for i in {1..10}; do
    creation_time=${exif_dates[$((i-1))]}
    duration=$((10+i))
    file_name_index=`printf "%02d" $i`

    create_vid $duration "$creation_time" "$current_dir/video-$file_name_index.mp4"

    img_creation_time=`echo ${exif_dates[$((i-1))]} | sed -e "s/-/:/g"`
    img_bg_arg=$((i-1))

    create_img $i "#FF00F$img_bg_arg" "$img_creation_time" "$current_dir/image-$file_name_index.jpg"
done

# Archivos que colisionen con mismo checksum (con mismo nombre y mismo exif dates)
rsync -qa $DIR_SAMPLES/01-base/ $DIR_SAMPLES/03-base-clone/

# Archivos .trashed
current_dir=$DIR_SAMPLES/04-trashed-files
mkdir -p $current_dir

for i in {1..10}; do
    creation_time=${exif_dates[$((i-1))]}
    duration=$((20+i))
    file_name_index=`printf "%02d" $i`

    create_vid $duration "$creation_time" "$current_dir/.trashed-00000000$file_name_index-video-$file_name_index.mp4"

    img_creation_time=`echo ${exif_dates[$((i-1))]} | sed -e "s/-/:/g"`
    img_bg_arg=$((i-1))

    create_img $i "#00FFF$img_bg_arg" "$img_creation_time" "$current_dir/.trashed-00000000$file_name_index-image-$file_name_index.jpg"
done

# Archivos con los distintos nombres con fechas soportados
current_dir=$DIR_SAMPLES/05-no-exif-with-names
mkdir -p $current_dir

#   format: IMG20231229232507
#   3, IMG|VID
#   14, 20231229232507
create_vid 30 "" "$current_dir/VID20231229232507.mp4"
create_img 1 "#FFFF00" "" "$current_dir/IMG20231229232507.jpg"

#   format: IMG_20231229_232507
#   4, IMG_|VID_
#   15, 20231229_232507

create_vid 31 "" "$current_dir/VID_20231229_232507.mp4"
create_img 2 "#FFFF00" "" "$current_dir/IMG_20231229_232507.jpg"

#   format: 2013-03-17-19-57-16_photo
#           2013-03-17-19-57-50_deco
#   4, 2013-03-17-19-57-50

create_vid 32 "" "$current_dir/2013-12-29-23-25-07_video.mp4"
create_img 3 "#FFFF00" "" "$current_dir/2013-12-29-23-25-07_photo.jpg"

#   format: _20140209_174329
#           CYMERA_20130615_103530
#           image_20161021_165225
#           PANO_20130320_160358
#           Pixlr_20160411150815984
#           pixlr_20171021160935846
#           Screenshot_20160629-213115
#           TRIM_20131203_183531
#           ???-20140320-WA0002.jpg
#           Screenshot_2012-11-26-10-31-14.png
#   X, XXXX
#   8, 20231229

create_vid 33 "" "$current_dir/ALTER_20231229_232507.mp4"
create_img 4 "#FFFF00" "" "$current_dir/ALTER_20231229_232507.jpg"

create_vid 34 "" "$current_dir/ALTER_20231229232507.mp4"
create_img 5 "#FFFF00" "" "$current_dir/ALTER_20231229232507.jpg"

create_vid 35 "" "$current_dir/ALTER_20231229-232507.mp4"
create_img 6 "#FFFF00" "" "$current_dir/ALTER_20231229-232507.jpg"

create_vid 36 "" "$current_dir/ALTER_20231229-WA0002.mp4"
create_img 7 "#FFFF00" "" "$current_dir/ALTER_20231229-WA0002.jpg"

create_vid 37 "" "$current_dir/ALTER_2023-12-29-23-25-07.mp4"
create_img 8 "#FFFF00" "" "$current_dir/ALTER_2023-12-29-23-25-07.jpg"

# Archivos sin exif con fechas por momento de modificacion
current_dir=$DIR_SAMPLES/06-no-exif-modified-file-date
mkdir -p $current_dir

for i in {1..10}; do
    modification_time=`echo ${exif_dates[$((i-1))]} | sed -e 's/[- :]//g' -e 's/\(.*\)\(..\)$/\1.\2/'`
    duration=$i
    file_name_index=`printf "%02d" $i`
    
    create_vid $duration "" "$current_dir/video-$file_name_index.mp4"
    touch -t $modification_time "$current_dir/video-$file_name_index.mp4"

    img_bg_arg=$((i-1))

    create_img $i "#FFFFF$img_bg_arg" "" "$current_dir/image-$file_name_index.jpg"
    touch -t $modification_time "$current_dir/image-$file_name_index.jpg"
done

# Archivos no-media
current_dir=$DIR_SAMPLES/07-no-media
mkdir -p $current_dir

for i in {1..10}; do
    file_name_index=`printf "%02d" $i`
    modification_time=`echo ${exif_dates[$((i-1))]} | sed -e 's/[- :]//g' -e 's/\(.*\)\(..\)$/\1.\2/'`
    output_file="$current_dir/text-$file_name_index.txt"

    echo " * Generando $output_file..."
    echo "$i" > $output_file
    touch -t $modification_time $output_file
done

# Sacando el espacio usado
du -sh $DIR_SAMPLES/