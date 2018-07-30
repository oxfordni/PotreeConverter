#include <experimental/filesystem>
#include "LOCBPointReader.h"

#include "stuff.h"

namespace fs = std::experimental::filesystem;

namespace Potree{

LOCBPointReader::LOCBPointReader(string path){

	if(fs::is_directory(path)){
		// if directory is specified, find all las and laz files inside directory

		for(fs::directory_iterator it(path); it != fs::directory_iterator(); it++){
			fs::path filepath = it->path();
			if(fs::is_regular_file(filepath)){
				if(icompare(fs::path(filepath).extension().string(), ".locb")){
					files.push_back(filepath.string());
				}
			}
		}
	}else{
		files.push_back(path);
	}

	// open first file
	currentFile = files.begin();
	reader = new LOCBReader(*currentFile);
	aabb = reader->getAABB();

}

LOCBPointReader::~LOCBPointReader(){
	close();
}

void LOCBPointReader::close(){
	if(reader != NULL){
		reader->close();
		delete reader;
		reader = NULL;
	}
}

long long LOCBPointReader::numPoints(){
	long long points = reader->numPoints();
	return points;
}

bool LOCBPointReader::readNextPoint(){

	bool hasPoints = reader->readPoint();

	if(!hasPoints){
		// try to open next file, if available
		reader->close();
		delete reader;
		reader = NULL;

		currentFile++;

		if(currentFile != files.end()){
			reader = new LOCBReader(*currentFile);
			hasPoints = reader->readPoint();
			aabb = reader->getAABB();
		}
	}

	return hasPoints;
}

Point LOCBPointReader::getPoint(){
	Point const p = reader->GetPoint();
    return p;
}

AABB LOCBPointReader::getAABB(){
	return aabb;
}

}
