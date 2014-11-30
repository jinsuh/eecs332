% Inputs:
% 'filename': the image file containing the sample image (the texture to grow)
% 'winsize': the edge length of the window to match at each iteration (the window is (winsize x winsize) )
% (numRows, numCols): the size of the output image

% Outputs:
% 'Image': the output image (the synthesized texture)

function newImage = text_synth(fileName, winSize, numRows, numCols)

% maxErrThreshold = 0.1;
fileName = imread(fileName);
sample = im2double(fileName);

% [rows, cols, channels] = size(sample);
% 
% windowlessSize = [(rows - winSize + 1) (cols - winSize + 1)];
candidates = {};
count = 1;
for r = 1:size(fileName, 2)
   for c = 1:size(fileName, 1)
       if (r+winSize <= size(fileName, 2) + 1) && (c+winSize <= size(fileName, 1) + 1)
          candidates{count} = fileName(r:r+winSize - 1, c:c+winSize - 1, :);
          count = count + 1;
       else
           break;
       end
   end
end

% 1 2 3
% 4 5 6
% test(2, :) -> 4 5 6
newImage = uint8(zeros(numRows, numCols, 3));
for newRow = 1:winSize - 1:numRows-winSize
   for newCol = 1:winSize - 1:numCols-winSize
       fprintf('newRow: %d, newCol: %d \n', newRow, newCol);
       if newRow == 1 && newCol == 1 %first block
           num = randi(size(candidates, 2));
           minIndex = num;
           minBlock = candidates{num};
       elseif newRow == 1 %just check left
           minVal = intmax;
           minIndex = -1;
           for canIndex = 1:size(candidates, 2) % check all candidates for best fit
               cand = candidates{canIndex};
               rightPixels = newImage(1:winSize, newCol, :);
               leftPixels = cand(:, 1, :);
               diffVec = imabsdiff(rightPixels, leftPixels);
               res = sum(diffVec .* diffVec);
               res = res(:, :, 1) + res(:, :, 2) + res(:, :, 3);
               if res < minVal
                   minBlock = cand;
                   minVal = res;
                   minIndex = canIndex;
               end
           end
       elseif newCol == 1 %just check up
           minIndex = -1;
           minVal = intmax;
           for canIndex = 1:size(candidates, 2) % check all candidates for best fit
               cand = candidates{canIndex};
               upperPixels = newImage(newRow, 1:winSize, :);
               lowerPixels = cand(1, :, :);
               diffVec = imabsdiff(upperPixels, lowerPixels);
               res = sum(diffVec .* diffVec);
               res = res(:, :, 1) + res(:, :, 2) + res(:, :, 3);
               if res < minVal
                   minBlock = cand;
                   minVal = res;
                   minIndex = canIndex;
               end
           end
       else %check left and up
           minVal = intmax;
           minIndex = -1;
           for canIndex = 1:size(candidates, 2) % check all candidates for best fit
               cand = candidates{canIndex};
               upperPixels = newImage(newRow, 1:winSize, :);
               lowerPixels = cand(1, :, :);
               rightPixels = newImage(1:winSize, newCol, :);
               leftPixels = cand(:, 1, :);
               diffVec = imabsdiff(upperPixels, lowerPixels);
               diffVec2 = imabsdiff(rightPixels, leftPixels);
               res = sum(diffVec .* diffVec);
               res2 = sum(diffVec2 .* diffVec2);
               res = res(:, :, 1) + res(:, :, 2) + res(:, :, 3) + res2(:, :, 1) + res2(:, :, 2) + res2(:, :, 3);
               if res < minVal
                   minBlock = cand;
                   minVal = res;
                   minIndex = canIndex;
               end
           end
       end
       disp(minIndex);
       newImage(newRow:newRow + winSize - 1, newCol:newCol + winSize - 1, :) = minBlock;
%        disp(minBlock);
       if newCol + winSize - 1 > numCols - winSize %Do the last one in the col
           if newRow == 1 %top row
               minVal = intmax;
               minIndex = -1;
               for canIndex = 1:size(candidates, 2) % check all candidates for best fit
                   cand = candidates{canIndex};
                   rightPixels = newImage(1:winSize, newCol, :);
                   leftPixels = cand(:, 1, :);
                   diffVec = imabsdiff(rightPixels, leftPixels);
                   res = sum(diffVec .* diffVec);
                   res = res(:, :, 1) + res(:, :, 2) + res(:, :, 3);
                   if res < minVal
                       minBlock = cand;
                       minVal = res;
                       minIndex = canIndex;
                   end
               end
           else
               minVal = intmax;
               minIndex = -1;
               for canIndex = 1:size(candidates, 2) % check all candidates for best fit
                   cand = candidates{canIndex};
                   upperPixels = newImage(newRow, 1:winSize, :);
                   lowerPixels = cand(1, :, :);
                   rightPixels = newImage(1:winSize, newCol, :);
                   leftPixels = cand(:, 1, :);
                   diffVec = imabsdiff(upperPixels, lowerPixels);
                   diffVec2 = imabsdiff(rightPixels, leftPixels);
                   res = sum(diffVec .* diffVec);
                   res2 = sum(diffVec2 .* diffVec2);
                   res = res(:, :, 1) + res(:, :, 2) + res(:, :, 3) + res2(:, :, 1) + res2(:, :, 2) + res2(:, :, 3);
                   if res < minVal
                       minBlock = cand;
                       minVal = res;
                       minIndex = canIndex;
                   end
               end
           end
%            fprintf('new row: %d, new col: %d, num cols: %d, size window: %d\n', newRow, newCol, numCols, winSize);
%            fprintf('subtraction: %d, sizeMinBlock: %d', numCols - newCol - winSize, size(minBlock, 1));
           newImage(newRow:newRow + winSize - 1, newCol+winSize - 1:numCols, :) = minBlock(:, 1:numCols - newCol - winSize + 2, :);
       end
       if newRow + winSize - 1 > numRows - winSize %Do the last one in the row
           if newCol == 1 %top col
               minIndex = -1;
               minVal = intmax;
               for canIndex = 1:size(candidates, 2) % check all candidates for best fit
                   cand = candidates{canIndex};
                   upperPixels = newImage(newRow, 1:winSize, :);
                   lowerPixels = cand(1, :, :);
                   diffVec = imabsdiff(upperPixels, lowerPixels);
                   res = sum(diffVec .* diffVec);
                   res = res(:, :, 1) + res(:, :, 2) + res(:, :, 3);
                   if res < minVal
                       minBlock = cand;
                       minVal = res;
                       minIndex = canIndex;
                   end
               end
           else
               minVal = intmax;
               minIndex = -1;
               for canIndex = 1:size(candidates, 2) % check all candidates for best fit
                   cand = candidates{canIndex};
                   upperPixels = newImage(newRow, 1:winSize, :);
                   lowerPixels = cand(1, :, :);
                   rightPixels = newImage(1:winSize, newCol, :);
                   leftPixels = cand(:, 1, :);
                   diffVec = imabsdiff(upperPixels, lowerPixels);
                   diffVec2 = imabsdiff(rightPixels, leftPixels);
                   res = sum(diffVec .* diffVec);
                   res2 = sum(diffVec2 .* diffVec2);
                   res = res(:, :, 1) + res(:, :, 2) + res(:, :, 3) + res2(:, :, 1) + res2(:, :, 2) + res2(:, :, 3);
                   if res < minVal
                       minBlock = cand;
                       minVal = res;
                       minIndex = canIndex;
                   end
               end
           end
           newImage(newRow+winSize - 1:numRows, newCol:newCol + winSize - 1, :) = minBlock(1:numRows - newRow - winSize + 2, :, :);
       end
       if newRow + winSize - 1 > numRows - winSize && newCol + winSize - 1 > numCols - winSize
           minVal = intmax;
           minIndex = -1;
           for canIndex = 1:size(candidates, 2) % check all candidates for best fit
               cand = candidates{canIndex};
               upperPixels = newImage(newRow, 1:winSize, :);
               lowerPixels = cand(1, :, :);
               rightPixels = newImage(1:winSize, newCol, :);
               leftPixels = cand(:, 1, :);
               diffVec = imabsdiff(upperPixels, lowerPixels);
               diffVec2 = imabsdiff(rightPixels, leftPixels);
               res = sum(diffVec .* diffVec);
               res2 = sum(diffVec2 .* diffVec2);
               res = res(:, :, 1) + res(:, :, 2) + res(:, :, 3) + res2(:, :, 1) + res2(:, :, 2) + res2(:, :, 3);
               if res < minVal
                   minBlock = cand;
                   minVal = res;
                   minIndex = canIndex;
               end
           end
           newImage(newRow+winSize - 1:numRows, newCol + winSize - 1:numCols, :) = minBlock(1:numRows - newRow - winSize + 2, 1:numCols - newCol - winSize + 2, :);
       end
   end
end

imwrite(newImage, 'res_block.jpg');
end