function main()
    I = imread('test.bmp');
    I = rgb2gray(I);
    S = gaussian(I, 3, 3);
    [Gmag, Gdir] = imgradient(S);
    Gdir = Gdir + 180.0;
    imshowpair(Gmag, Gdir, 'montage');
    
    mag = nonMaximaSupression(Gmag, Gdir);
%     imshow(mag);
    [tLow, tHigh] = findThreshold(mag, 0.9);
    tLowMag = createThresholdMag(mag, tLow);
    tHighMag = createThresholdMag(mag, tHigh);
%     imshow(tHighMag);
end

function S = gaussian(I, N, sigma)
    Gmask = fspecial('gaussian', [N, N], sigma);
    S = conv2(double(I), double(Gmask), 'same');
end

function in = inBounds(tuple, width, height)
    row = tuple(1);
    col = tuple(2);
    in = (row >= 1 && row <= height && col >= 1 && col <= width);
end

function [tLow, tHigh] = findThreshold(mag, percent)
    histogram = zeros(100);
    [width, height] = size(mag);
    for i = 1:width
        for j = 1:height
            value = int8(round(mag(i, j) / 255.0 * 100)) + 1;
            histogram(value) = histogram(value) + 1;
        end
    end
    
    cummulativeSum = 0;
    
    sizeOfHistogram = size(histogram);
    
    for i = 1:sizeOfHistogram
        cummulativeSum = cummulativeSum + histogram(i);
        
        if cummulativeSum > width * height * percent
            temp = i;
            break
        end
    end
    
    tHigh = temp / 100.0;
    tLow = tHigh * 0.5;
end

function newImage = createThresholdMag(mag, threshold)
    [width, height] = size(mag);
    newImage = zeros(width, height);
    
    for i = 1:width
        for j = 1:height
            value = mag(i, j) / 255.0;
            if value > threshold
                newImage(i, j) = 255;
            else
                newImage(i, j) = 0;
            end
        end
    end
end

function mag = nonMaximaSupression(Gmag, Gdir)
    lut = [1, 0; 1, 1; 0, 1; -1, 1; -1, 0; -1, -1; 0, -1; 1, -1; 1, 0];

    [width,height] = size(Gmag);

    for i = 1:width
        for j = 1:height
            index = mod(int8(Gdir(i, j) / 45.0), 7) + 2 + 1;
            neighborA = [i, j] + lut(index,:);
            neighborB = [i, j] + neighborA .* -1;

            if inBounds(neighborA, width, height)
                neighborAGradient = Gmag(neighborA(1), neighborA(2));
            else
                neighborAGradient = -999999999999;
            end
            
            if inBounds(neighborB, width, height)
                neighborBGradient = Gmag(neighborB(1), neighborB(2));
            else
                neighborBGradient = -999999999999;
            end
            
            if neighborAGradient > Gmag(i, j) || neighborBGradient > Gmag(i, j)
                Gmag(i, j) = 0;
            end
        end
    end
    
    mag = Gmag;
end
    