function main(frames, nFrames)
	H = zeros(1);
	[height, width] = size(frames(:, :, 1, 1));

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

	% line = VideoWriter('line.avi');
	% line.FrameRate = 15;
	% open(line);

	count = 0;
	right = [zeros(height, width); zeros(height, width); zeros(height, width)];

	prevCol = -1;
	
	frame = frames(:, :, :, 1);

	redTopRow = 0;
	redBottomRow = 0;

	for r = 1:height
		for c = 1:width
			if isRed(frame, r, c) == 1
				redTopRow = r;
				r = height + 1;
				break
			end
		end
	end

	for r = height:-1:1
		for c = 1:width
			if isRed(frame, r, c) == 1
				imwrite(frame(r,c,:), 'frame.bmp');
				redBottomRow = r;
				r = 0;
				break
			end
		end
	end

	redTopRow = 60;%redTopRow - 5
	redBottomRow = 160;%redBottomRow + 5

	for i=1:nFrames
		fprintf('frame %d\n', i);
		frame = int32((frames(:, :, 1, i) + frames(:, :, 2, i) + frames(:, :, 3, i)) / 3);

		difference = generateDifferenceImage(frame, average);
		binary_image = generateBinaryImage(difference, 60);
		[row, col] = centroid(binary_image);
		
		if prevCol == -1
			prevCol = col;
		end

		frame = frames(:, :, :, i);

		% frame = drawLine(frame, col, 0, synthesizedTexture);
		
		if mod(count, 5) == 0
			imwrite(frames(redBottomRow:redBottomRow+18, col:col+18, :, 1), 'test.bmp');
			text_synth('test.bmp', 18, abs(redBottomRow - redTopRow), 40);
			synthesizedTexture = imread('res_block.jpg');
			for r = 1:abs(redBottomRow - redTopRow)
				for c = 1:(prevCol - col) + 4
					if isRed(frame, r, c) == 1
						% frame(r + 60, c + col, 1) = synthesizedTexture(r, c, 1);
						% frame(r + 60, c + col, 2) = synthesizedTexture(r, c, 2);
						% frame(r + 60, c + col, 3) = synthesizedTexture(r, c, 3);
						right(r + redTopRow, c + col, 1) = synthesizedTexture(r, c, 1);
						right(r + redTopRow, c + col, 2) = synthesizedTexture(r, c, 2);
						right(r + redTopRow, c + col, 3) = synthesizedTexture(r, c, 3);
					end
				end
			end
			
			for r = 1:height
				for c = 1:width
					if right(r, c, 1) ~= 0 && right(r, c, 2) ~= 0 && right(r, c, 3) ~= 0
						frame(r, c, 1) = right(r, c, 1);
						frame(r, c, 2) = right(r, c, 2);
						frame(r, c, 3) = right(r, c, 3);
					end
				end
			end
		end
		prevCol = col;
		% lineFrame = zeros(size(frame));
		% lineFrame = drawLine(lineFrame, col, 0);
		% fileName = sprintf('frame_%d.bmp',i);
		% imwrite(frame, fileName);
		% writeVideo(line, uint8(lineFrame));
		writeVideo(vid, frame);
		cout = count + 1;
	end
	close(vid);
end

function value = isRed(frame, r , c)
	value = (frame(r, c, 1) > 50 && frame(r, c, 2) < 150 && frame(r, c, 3) < 120);
end

function image = drawLine(image, r, theta)
	[height, width] = size(image);

	for row = 1:height
		for col = 1:width
			if r == int32(col * cos(theta) + row * sin(theta))
				image(row, col, 1) = 255;
				image(row, col, 2) = 0;
				image(row, col, 3) = 0;
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