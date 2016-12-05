#!/bin/sh

# algorithm options:
# 	"FM^3 (OGDF)"
# 	"Fast Multipole Embedder (OGDF)"
# 	"Fast Multipole Multilevel Embedder (OGDF)"
# 	"Pivot MDS (OGDF)"
# 	"GRIP" (kind of slow for larger data sets)
# 	- (weird result) "Frutcherman Reingold (OGDF)"
# 	- (weird result) "GEM Frick (OGDF)"
# 	- (slow) "GEM (Frick)"
# 	- (slow) "Bertault (OGDF)"
# 	- (slow) "Kamada Kawai (OGDF)"
# 	- (slow) "LinLog"
# 	- (slow) "Upward Planarization (OGDF)"
# 	- (slow) "Visibility (OGDF)"
# 	- (InsufficientMemoryException) "Stress Majorization (OGDF)"
# 	- (Python stops working?) "Sugiyama (OGDF)"

# re-generates a set of coordinates
# example:
# here, <532> is the data set number
# python backend/run_layout.py 532 "FM^3 (OGDF)"
cd backend
python run_layout.py 225 "FM^3 (OGDF)"
cd ..

# renders the png
./phantomjs docs/generator.js 

printf "Done!\n"
