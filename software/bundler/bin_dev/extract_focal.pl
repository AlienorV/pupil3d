#!/usr/bin/perl

# extract_focal.pl
#  -- Tool for preparing a directory of images for bundler by computing 
#     focal lengths from Exif tags
# Copyright 2005-2008 Noah Snavely

# Set this variable to your base install path (e.g., /cygdrive/c/programs/bundler)
#$BASE_PATH = "/Users/marc/fieldwork/temp/bundler/bundler-v0.2-source/";
$BASE_PATH="/Volumes/HD_Two/Users/Will/Documents/2012/MIT/Thesis/Repository/trunk/Software/Structure_From_Motion/bundler-v0.4-source";

$JHEAD_EXE = "$BASE_PATH/bin/jhead";
$OUT_DIR = "./prepare";

if ($BASE_PATH eq "TODO") {
    print "Please modify this script (extract_focal.pl) with the base path of your bundler installation.\n";
    exit;
}

$SCALE=1.0;

%ccd_widths =
    ("NIKON E4500"                      => 7.176,  # 1/1.8"
     "Nokia N80"                        => 5.27,   # 1/2.7"
     "Nokia N93"                        => 4.536,  # 1/3.1"
     "Nokia N95"                        => 5.7,    # 1/2.7"
     "Canon Canon PowerShot A20"        => 7.176,  # 1/1.8"
     "Canon Canon PowerShot A40"        => 5.27,   # 1/2.7"
     "Canon Canon PowerShot A70"        => 5.27,   # 1/2.7"
     "Canon Canon PowerShot A75"        => 5.27,   # 1/2.7"
     "Canon Canon PowerShot A60"        => 5.27,   # 1/2.7"
     "Canon Canon PowerShot A80"        => 7.176,  # 1/1.8"
     "Canon Canon PowerShot A85"        => 5.27,   # 1/2.7"
     "Canon Canon PowerShot A95"        => 7.176,  # 1/1.8"
     "Canon Canon PowerShot S80"        => 7.176,  # 1/1.8"
     "Canon Canon PowerShot Pro1"       => 8.8,    # 2/3"
     "Canon Canon PowerShot A510"       => 5.76,   # 1/2.5"
     "Canon Canon PowerShot A620"       => 7.176,  # 1/1.8"
     "Canon Canon PowerShot A640"       => 7.176,  # 1/1.8"
     "Canon Canon PowerShot A710 IS"    => 5.76,   # 1/2.5"
     "Canon Canon PowerShot SD100"      => 5.27,   # 1/2.7"
     "Canon Canon PowerShot SD110"      => 5.27,   # 1/2.7"
     "Canon Canon PowerShot SD300"      => 5.76,   # 1/2.5"
     "Canon Canon PowerShot SD400"      => 5.76,   # 1/2.5"
     "Canon Canon PowerShot SD450"      => 5.76,   # 1/2.5"
     "Canon Canon PowerShot SD500"      => 7.176,  # 1/1.8"
     "Canon Canon PowerShot SD550"      => 7.176,  # 1/1.8"
     "Canon Canon DIGITAL IXUS 750"     => 7.176,  # 1/1.8"
     "Canon Canon PowerShot SD600"      => 5.76,   # 1/2.5"
     "Canon Canon PowerShot SD630"      => 5.76,   # 1/2.5"
     "Canon Canon PowerShot SD800 IS"   => 5.76,   # 1/2.5"
     "Canon Canon PowerShot S1 IS"      => 5.27,   # 1/2.7"
     "Canon Canon PowerShot A530"       => 5.76,   # 1/2.5"
     "Canon Canon PowerShot A700"       => 5.76,   # 1/2.5"
     "Canon PowerShot A510"             => 5.76,   # 1/2.5" ???
     "Canon Canon PowerShot S200"       => 5.27,   # 1/2.7"
     "Canon Canon PowerShot A520"       => 5.76,   # 1/2.5"
     "Canon PowerShot S30"              => 7.176,  # 1/1.8"
     "Canon Canon EOS-1Ds Mark II"      => 35.95,   
     "Canon Canon EOS 20D"              => 22.5,
     "Canon Canon EOS 30D"              => 22.5,
     "Canon Canon EOS 5D"               => 35.8,
     "Canon Canon PowerShot S2 IS"      => 5.76,   # 1/2.5"
     "Canon Canon PowerShot S3 IS"      => 5.76,   # 1/2.5"
     "Canon Canon PowerShot S30"        => 7.176,  # 1/1.8"
     "Canon Canon PowerShot S40"        => 7.176,  # 1/1.8"
     "Canon Canon PowerShot S45"        => 7.176,  # 1/1.8"
     "Canon Canon PowerShot S50"        => 7.176,  # 1/1.8"
     "Canon Canon PowerShot S60"        => 7.176,  # 1/1.8"
     "Canon Canon PowerShot S70"        => 7.176,  # 1/1.8"
     "Canon Canon PowerShot S400"       => 7.176,  # 1/1.8"
     "Canon Canon PowerShot S410"       => 7.176,  # 1/1.8"
     "Canon Canon PowerShot S500"       => 7.176,  # 1/1.8"
     "Canon Canon PowerShot S110"       => 5.27,   # 1/2.7"
     "Canon Canon PowerShot G6"         => 7.176,  # 1/1.8"
     "Canon Canon PowerShot G1"         => 7.176,  # 1/1.8"
     "Canon Canon PowerShot G2"         => 7.176,  # 1/1.8"
     "Canon Canon PowerShot G3"         => 7.176,  # 1/1.8"
     "Canon Canon PowerShot G5"         => 7.176,  # 1/1.8"
     "Canon Canon PowerShot G9"         => 7.600,  # 1/1.7"
     "Canon Canon DIGITAL IXUS 40"      => 5.76,   # 1/2.5"
     "Canon Canon DIGITAL IXUS 50"      => 5.76,   # 1/2.5"
     "Canon Canon DIGITAL IXUS 55"      => 5.76,   # 1/2.5"
     "Canon Canon DIGITAL IXUS 60"      => 5.76,   # 1/2.5"
     "Canon Canon DIGITAL IXUS 65"      => 5.76,   # 1/2.5"
     "Canon Canon DIGITAL IXUS 400"     => 7.176,  # 1/1.8"
     "Canon Canon DIGITAL IXUS 500"     => 7.176,  # 1/1.8"
     "Canon Canon DIGITAL IXUS 800 IS"  => 5.76,   # 1/2.5"
     "Canon Canon DIGITAL IXUS II"      => 5.27,   # 1/2.7"
     "Canon Canon IXY DIGITAL 600"      => 7.176,  # 1/1.8"
     "OLYMPUS CORPORATION C750UZ"       => 5.27,   # 1/2.7"
     "OLYMPUS OPTICAL CO.,LTD C211Z"    => 5.27,   # 1/2.7"
     "OLYMPUS X100,D540Z,C310Z"         => 5.27,   # 1/2.7"
     "OLYMPUS OPTICAL CO.,LTD X-2,C-50Z       " => 7.176, # 1/1.8"
     "OLYMPUS_IMAGING_CORP.   X450,D535Z,C370Z" => 5.27, # 1/2.7" 
     "OLYMPUS CORPORATION     C-5000Z         "      => 7.176,  # 1/1.8"
     "OLYMPUS OPTICAL CO.,LTD C4100Z,C4000Z" => 7.176,  # 1/1.8" 
     "OLYMPUS CORPORATION C765UZ"       => 5.76,   # 1//2.5"
     "OLYMPUS CORPORATION C8080WZ"      => 8.80,   # 2/3"
     "OLYMPUS IMAGING CORP.   E-500           " => 17.3,  # 4/3?
     "OLYMPUS IMAGING CORP.   FE115,X715" => 5.76, # 1/2.5"
     "CASIO COMPUTER CO.,LTD. EX-S500"  => 5.76,   # 1/2.5"
     "CASIO COMPUTER CO.,LTD  EX-Z30 "  => 5.76,   # 1/2.5 "
     "CASIO COMPUTER CO.,LTD. EX-Z600"  => 5.76,   # 1/2.5"
     "CASIO COMPUTER CO.,LTD. EX-Z60     " => 7.176, # 1/1.8"
     "CASIO COMPUTER CO.,LTD  EX-Z750"     => 7.176, # 1/1.8"
     "CASIO COMPUTER CO.,LTD. EX-Z1000   " => 7.716, # 1/1.8"
     "KONICA MINOLTA DiMAGE A200"       => 8.80,   # 2/3"
     "KONICA MINOLTA DiMAGE X1"         => 7.176,  # 1/1.8"
     "Minolta Co., Ltd. DiMAGE Xi"      => 5.27,   # 1/2.7"
     "KONICA MILOLTA  DYNAX 5D"          => 23.5,
     "KONICA MINOLTA  DYNAX 5D"          => 23.5,
     "Minolta Co., Ltd. DiMAGE Xt"      => 5.27,   # 1/2.7"
     "Minolta Co., Ltd. DiMAGE F100"    => 7.176,  # 1/2.7"
     "RICOH CaplioG3 modelM"            => 5.27,   # 1/2.7"
     "RICOH       Caplio GX      "      => 7.176,  # 1/1.8"
     "NIKON E990"                       => 7.176,  # 1/1.8"
     "NIKON E5200"                      => 7.176,  # 1/1.8"
     "NIKON E4600"                      => 5.76,   # 1/2.5"
     "NIKON E4200"                      => 7.176,  # 1/1.8"
     "NIKON E5000"                      => 8.80,   # 2/3"
     "NIKON E5600"                      => 5.76,   # 1/2.5"
     "NIKON E5700"                      => 8.80,   # 2/3"
     "NIKON E5900"                      => 7.176,  # 1/1.8"
     "NIKON S1  "                       => 5.76,   # 1/2.5"
     "EASTMAN KODAK COMPANY KODAK CX7330 ZOOM DIGITAL CAMERA" => 5.27, # 1/2.7"
     "EASTMAN KODAK COMPANY KODAK DX7630 ZOOM DIGITAL CAMERA" => 7.176, # 1/1.8"
     "EASTMAN KODAK COMPANY KODAK DX4900 ZOOM DIGITAL CAMERA" => 7.176, # 1/1.8"
     "EASTMAN KODAK COMPANY KODAK DX3900 ZOOM DIGITAL CAMERA" => 7.176, # 1/1.8"
     "EASTMAN KODAK COMPANY KODAK DX6340 ZOOM DIGITAL CAMERA" => 5.27, # 1/2.7"
     "EASTMAN KODAK COMPANY KODAK CX7530 ZOOM DIGITAL CAMERA" => 5.76, # 1/2.5"
     "EASTMAN KODAK COMPANY KODAK DX6490 ZOOM DIGITAL CAMERA" => 5.76, # 1/2.5"
     "EASTMAN KODAK COMPANY KODAK Z700 ZOOM DIGITAL CAMERA" => 5.76, # 1/2.5"
     "NIKON E2500"                      => 5.27,   # 1/2.7"
     "NIKON E5400"                      => 7.176,  # 1/1.8"
     "NIKON E2500"                      => 5.27,   # 1/2.7"
     "NIKON E995"                       => 7.176,  # 1/1.8"
     "NIKON E7900"                      => 7.176,  # 1/1.8"
     "NIKON E3100"                      => 5.27,   # 1/2.7"
     "NIKON E3700"                      => 5.27,   # 1/2.7"
     "NIKON E775"                       => 5.27,   # 1/2.7"
     "NIKON E8800"                      => 8.80,   # 2/3"
     "NIKON E7600"                      => 7.176,  # 1/1.8"
     "NIKON COOLPIX S4"                 => 5.76,   # 1/2.5"
     "NIKON COOLPIX L3"                 => 5.76,   # 1/2.5"
     "NIKON CORPORATION NIKON D1H"      => 23.7,
     "NIKON CORPORATION NIKON D200"     => 23.6,
     "NIKON CORPORATION NIKON D2X"      => 23.7,
     "NIKON CORPORATION NIKON D2H"      => 23.3,
     "NIKON CORPORATION NIKON D100 "    => 23.7,
     "NIKON CORPORATION NIKON D100"     => 23.7,
     "NIKON CORPORATION NIKON D40"      => 23.7,
     "NIKON CORPORATION NIKON D80"      => 23.6,
     "Konica Minolta Camera, Inc. DiMAGE A2" => 8.80, # 2/3"
     "Konica Minolta Camera, Inc. DiMAGE Z2" => 5.76, # 1/2.5"
     "Minolta Co., Ltd. DiMAGE Z1" => 5.27, # 1/2.7" 
     "PENTAX Corporation PENTAX Optio S50" => 5.76, # 1/2.5"
     "PENTAX Corporation PENTAX Optio S40" => 5.76, # 1/2.5"
     "PENTAX Corporation PENTAX Optio E10" => 5.76, # 1/2.5"
     "PENTAX Corporation PENTAX Optio 450" => 7.176, # 1/1.8"
     "PENTAX Corporation PENTAX Optio 550" => 7.176, # 1/1.8"
     "PENTAX Corporation  PENTAX *ist DS2    "   => 23.5,
     "PENTAX Corporation  PENTAX *ist DS     "   => 23.5,
     "PENTAX Corporation  PENTAX *ist DL     "   => 23.5,
     "PENTAX Corporation  PENTAX Optio S5i " => 5.76, # 1/2.5" 
     "PENTAX Corporation  PENTAX Optio S4"   => 5.76, # 1/2.5" 
     "PENTAX Corporation  PENTAX Optio SV    "   => 5.76, # 1/2.5" 
     "Asahi Optical Co.,Ltd.  PENTAX Optio330RS" => 7.176, # 1/1.8"
     "FUJIFILM FinePix F450   "            => 5.76,   # 1/2.5"
     "FUJIFILM FinePix E500   "            => 5.76,   # 1/2.5" 
     "FUJIFILM FinePix E550   "            => 7.600,  # 1/1.7" 
     "FUJIFILM FinePix40i"                 => 7.600,  # 1/1.7" 
     "FUJIFILM FinePix E510   "            => 5.76,   # 1/2.5"
     "FUJIFILM FinePix Z2     "              => 5.76,   # 1/2.5"
     "FUJIFILM FinePix A600   "         => 7.600,  # 1/1.7"
     "FUJIFILM FinePix A310  "          => 5.27,   # 1/2.7"
     "FUJIFILM FinePix A330   "         => 5.27,   # 1/2.7"
     "FUJIFILM FinePix F10    "         => 7.600, # 1/1.7"
     "FUJIFILM FinePix2600Zoom"         => 5.27,   # 1/2.7"
     "FUJIFILM FinePix S5500  "         => 5.27,   # 1/2.7"
     "FUJIFILM FinePix S5000 "          => 5.27,   # 1/2.7"
     "FUJIFILM FinePix S6500fd"         => 7.600,  # 1/1.7"
     "FUJIFILM FinePix S3Pro  "         => 23.0,
     "FUJIFILM FinePix F30    "         => 7.600,  # 1/1.7"
     "FUJIFILM FinePix S7000 "          => 7.600,  # 1/1.7"
     "Samsung  Digimax 301"             => 5.27,   # 1/2.7"
     "SAMSUNG TECHWIN Pro 815    "      => 8.80,   # 2/3"
     "Samsung Techwin <Digimax i5, Samsung #1>" => 5.76,   # 1/2.5"
     "SONY DSC-P12"                     => 7.176,  # 1/1.8"
     "SONY DSC-P52"                     => 5.27,   # 1/2.7"
     "SONY DSC-P150"                    => 7.176,  # 1/1.8"
     "SONY DSC-V1"                      => 7.176,  # 1/1.8"
     "SONY DSC-W7"                      => 7.176,  # 1/1.8"
     "SONY DSC-W5"                      => 7.176,  # 1/1.8"
     "SONY DSC-W30"                     => 5.760,  # 1/2.5"
     "SONY DSC-R1"                      => 21.5,
     "SONY DSC-F828"                    => 8.80,   # 2/3"
     "SONY DSC-P100"                    => 7.176,  # 1/1.8"
     "SONY DSC-S600"                    => 5.760,  # 1/2.5"
     "SONY DSC-T9"                      => 7.18,
     "SONY DSC-N12"                     => 7.176,  # 1/1.8"
     # "SONY DSC-T1"                      => 7.66,   # 1/2.4"
     "Panasonic DMC-LC33"               => 5.760,  # 1/2.5"
     "Panasonic DMC-FZ5"                => 5.760,  # 1/2.5"
     "Panasonic DMC-FZ20"               => 5.760,  # 1/2.5"
     "Panasonic DMC-LC1"                => 8.80,   # 2/3"
     "Panasonic DMC-FX01"               => 5.76,   # 1/2.5"
     "Panasonic DMC-LZ2"                => 5.76,   # 1/2.5"
     "Panasonic DMC-FZ7"                => 5.76,   # 1/2.5"
     "Panasonic DMC-FZ30"               => 7.176,  # 1/1.8"
     "Hewlett-Packard hp PhotoSmart 43x series" => 5.27,  # 1/2.7"
     "Hewlett-Packard hp 635 Digital Camera" => 4.54, # 1/3.2"
     "Hewlett-Packard HP PhotoSmart C945 (V01.61) " => 7.176, # 1/1.8"
     "Hewlett-Packard HP PhotoSmart R707 (V01.00) " => 7.176, # 1/1.8"
     "EASTMAN KODAK COMPANY KODAK Z740 ZOOM DIGITAL CAMERA" => 5.76, # 1/2.5" ?
     "NIKON E7900"                      => 7.176,  # 1/1.8"
     "SONY DSC-P200"                    => 7.176,   # 1/1.8");
     "Canon EOS DIGITAL REBEL"          => 22.66,
     "Canon Canon EOS DIGITAL REBEL"     => 22.66,
     "Canon Canon EOS DIGITAL REBEL XT"  => 22.2,
     "Canon Canon EOS DIGITAL REBEL XTi" => 22.2,
     "Canon EOS 300D DIGITAL"            => 22.66,
     "Canon Canon EOS 400D DIGITAL"     => 22.2,
     "Canon Canon EOS Kiss Digital"     => 22.66,
     "Canon Canon EOS 300D DIGITAL"     => 22.66,
     "Canon Canon EOS-1D Mark II"       => 28.7,
     "Canon Canon EOS 10D"              => 22.7,
     "Canon Canon EOS 350D DIGITAL"     => 22.2,
     "NIKON CORPORATION NIKON D70s"     => 23.7,
     "NIKON CORPORATION NIKON D70"      => 23.7,
     "NIKON CORPORATION NIKON D50"      => 23.7,
     "NIKON E4300"                      => 7.18,
     "NIKON E3200"                      => 5.27,
     "OLYMPUS CORPORATION     X-3,C-60Z       " => 7.176, # 1.8"
     "OLYMPUS IMAGING CORP. X550,D545Z,C480Z" => 5.76, # 1/2.5" 
     "OLYMPUS OPTICAL CO.,LTD C300Z,D550Z" => 5.4,
     "OLYMPUS OPTICAL CO.,LTD C750UZ"   => 5.27,  # 1/2.7"
     "OLYMPUS CORPORATION X250,D560Z,C350Z" => 5.76, # 1/2.5" 
     "OLYMPUS OPTICAL CO.,LTD C2Z,D520Z,C220Z " => 4.54, # 1/3.2"
     "OLYMPUS CORPORATION C5060WZ"      => 7.176, # 1/1.8"
     "OLYMPUS OPTICAL CO.,LTD C2040Z"   => 6.40,  # 1/2"
     "OLYMPUS OPTICAL CO.,LTD C3000Z"   => 7.176, # 1/1.8"
     "OLYMPUS IMAGING CORP. SP310"      => 7.176, # 1/1.8"
     "SONY DSC-P73" => 5.27,
     "Apple iPhone 3GS" =>	3.626, # 1/4"
     "Apple iPhone 4" =>	4.592, # 1/3.2"
     "CASIO COMPUTER CO.,LTD. EX-Z850    " => 7.176);

`mkdir $OUT_DIR`;
`rm -f $OUT_DIR/list.txt`;

print "$#ARGV\n";
$IMAGE_LIST = "";
if ($#ARGV > -1) {
    $IMAGE_LIST = $ARGV[0];
}

$IMAGE_DIR = ".";
if ($#ARGV > 0) {
    $IMAGE_DIR = $ARGV[1];
}

printf("Image list is %s\n", $IMAGE_LIST);

if ($IMAGE_LIST eq "") {
    @images = split(/\n/, `ls -1 $IMAGE_DIR | egrep "\.jpg|\.JPG"`);
} else {
    if ($IMAGE_DIR eq ".") {
        @images = split(/\n/, `awk '{print \$0}' $IMAGE_LIST`);
    } else {
        @images = split(/\n/, `awk '{print "$IMAGE_DIR/" \$0}' $IMAGE_LIST`);
    }
}

$num_output_images = 0;
foreach $img (@images) {
    printf("[Extracting exif tags from image %s]\n", $img);

    $make_line = `$JHEAD_EXE $img | grep "Camera make"`;
    $make_line =~ s/\r?\n$//;

    ($make) = $make_line =~ /: (.*)$/;

    $model_line = `$JHEAD_EXE $img | grep "Camera model"`;
    $model_line =~ s/\r?\n$//;
    ($model) = $model_line =~ /: (.*)$/;

    # Grab focal length
    $focal_line = `$JHEAD_EXE $img | grep "Focal length" | awk '{print \$4}'`;
    $focal_line =~ s/\r?\n$//;
    ($focal_mm) = $focal_line =~ /(.*)mm/;
    printf("  [Focal length = %0.3fmm]\n", $focal_mm);

    # Grab CCD width

    $str = sprintf("%s %s", $make, $model);
    $ccd_width_mm = $ccd_widths{$str};
    # printf("[Looking up %s, got %s\n", $str, $ccd_width_mm);

    if ($ccd_width_mm == 0) {
        printf("[Couldn't find CCD width for camera %s]\n", $str);
	$ccd_width_line = 
	    `$JHEAD_EXE $img | grep "CCD width" | awk '{print \$4}'`;
	($ccd_width_mm) = $ccd_width_line =~ /(.*)mm/;

	$ccd_width_line =~ s/\r?\n$//;

        if ($ccd_width_mm != 0) {
            printf("[Found in EXIF tags]\n");
        }
    }

    printf("  [CCD width = %0.3fmm]\n", $ccd_width_mm);

    # Grab resolution
    $resolution_line = `$JHEAD_EXE $img | grep "Resolution"`;
    $resolution_line =~ s/\r?\n$//;

    ($res_x, $res_y) = $resolution_line =~ /: ([0-9]*) x ([0-9]*)/;
    printf("  [Resolution = %d x %d]\n", $res_x, $res_y);

    # Check that we got everything we need
#    if ($focal_mm == 0 || $ccd_width_mm == 0 || $res_x == 0) {
#	printf("  [** Couldn't extract required fields, stop]\n");
#
#	if ($model ne "") {
#	    printf("  [** $img: Couldn't find info on model %s %s]\n", 
#		   $make, $model);
#	}
#
#	next;
#    }

    if ($focal_mm == 0 || $ccd_width_mm == 0 || $res_x == 0) {
	$has_focal = 0;
    } else {
	$has_focal = 1;
    }

    if ($res_x < $res_y) {
	# Aspect ratio is wrong
	$tmp = $res_x;
	$res_x = $res_y;
	$res_y = $tmp;
    }

    # Convert to bmp and pgm
    $basename = `echo $img | sed 's/.[jJ][pP][gG]//'`;
    chomp($basename);

    if ($has_focal == 1) {
	# Compute focal length in pixels
	$focal_pixels = $res_x * ($focal_mm / $ccd_width_mm);
	printf("  [Focal length (pixels) = %0.3f\n", $focal_pixels);
	$line = sprintf("%s.jpg 0 %0.5f", $basename, $SCALE * $focal_pixels);
    } else {
	$line = sprintf("%s.jpg 0 %0.5f", $basename, 100.0);
#	$line = sprintf("%s.jpg", $basename);
    }

    `echo $line >> $OUT_DIR/list.txt`;
    $num_output_images++;
}

printf("[Found %d good images]\n", $num_output_images);
