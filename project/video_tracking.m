function main(frames, nFrames)
	H = zeros(1);
	[height, width] = size(frames(:, :, 1, 1));

	imwrite(frames(13:75, 13:75, :, 1), 'test.bmp');
	text_synth('test.bmp', 50, 240, 320);
	synthesizedTexture = imread('res_block.jpg');

	% generate average
	for i=1:(int32(nFrames)/10 - 1)
		fprintf('frame %d\n', i * 10);
		frame = int32((frames(:, :, 1, i*10) + frames(:, :, 2, i*10) + frames(:, :, 3, i*10)) / 3);
		H = generateAverageHistogram(frame, H);
	end

	average = zeros(height, width);
	for row = 1:height
		for col = 1:width
			maxPixelFrequency = 0;
			maxPixelValue = 0;

			pixels = H(row, col, :);

			pixels_size = size(pixels);
			pixels_size = pixels_size(3);

			for k = 1:pixels_size
				frequency = pixels(k);
				if frequency > maxPixelFrequency
					maxPixelFrequency = frequency;
					maxPixelValue = k;
				end
			end

			average(row, col) = maxPixelValue / 255.0;
		end
	end

	fileName = sprintf('average.bmp');
	imwrite(average, fileName);

	vid = VideoWriter('output.avi');
	vid.FrameRate = 15;
	open(vid);

	for i=1:nFrames
		fprintf('frame %d\n', i);
		frame = int32((frames(:, :, 1, i) + frames(:, :, 2, i) + frames(:, :, 3, i)) / 3);

		difference = generateDifferenceImage(frame, average);
		binary_image = generateBinaryImage(difference, 60);
		[row, col] = centroid(binary_image);
		
		frame = frames(:, :, :, i);
		% frame = drawLine(frame, col, 0, synthesizedTexture);

		for r = 60:130
			for c = col:width - 30
				% if frame(r, c, 1) > 120 && frame(r, c, 2) < 120 && frame(r, c, 3) < 120
				frame(r, c, 1) = 0;
				frame(r, c, 2) = 0;
				frame(r, c, 3) = 255;
				% end
			end
		end

		% fileName = sprintf('frame_%d.bmp',i);
		% imwrite(frame, fileName);
		writeVideo(vid, frame);
	end
	close(vid);
end

function image = drawLine(image, r, theta, synthesizedTexture)
	[height, width] = size(image);

	for row = 1:height
		for col = 1:width
			if r == int32(col * cos(theta) + row * sin(theta))
				image(row, col, 1) = 255;
				image(row, col, 2) = 0;
				image(row, col, 3) = 0;
				% frame(row, col, :)
			end
		end
	end
end

function [row, col] = centroid(image)
	[height, width] = size(image);

	rowSum = 0;
	colSum = 0;

	nonZeroSum = 0;

	for row = 1:height
		for col = 1:width
			if image(row, col) ~= 0
				rowSum = rowSum + row;
				colSum = colSum + col;
				nonZeroSum = nonZeroSum + 1;
			end
		end
	end

	row = int32(rowSum / nonZeroSum);
	col = int32(colSum / nonZeroSum);
end

function binary_image = generateBinaryImage(image, threshold)
	[height, width] = size(image);

	binary_image = zeros(height, width);
	minPixelValue = min(image(:));
	% abs(minPixelValue) + max(image(:))

	for row = 1:height
		for col = 1:width
			if image(row, col) + abs(minPixelValue) > threshold
				binary_image(row, col) = 1;
			else
				binary_image(row, col) = 0;
			end
		end
	end
end

function difference = generateDifferenceImage(frame, average)
	difference = double(average) - double(frame);
	difference = gaussian(difference, 4, 4);
end

function S = gaussian(I, N, sigma)
	Gmask = fspecial('gaussian', [N, N], sigma);
	S = conv2(double(I), double(Gmask), 'same');
end

function H = generateAverageHistogram(frame, H)
	[height, width] = size(frame);
	for row = 1:height
		for col = 1:width
			pixel = frame(row, col) + 1;
			try
				H(row, col, pixel) = H(row, col, pixel) + 1;
			catch err
				H(row, col, pixel) = 1;
			end
		end
	end
end