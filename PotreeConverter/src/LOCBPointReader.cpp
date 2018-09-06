#include "LOCBPointReader.h"
#include "stuff.h"

namespace Potree{

LOCBPointReader::LOCBPointReader(string path){

	reader = new LOCBReader(path);
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
		close();
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
