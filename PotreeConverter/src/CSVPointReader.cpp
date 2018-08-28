#include "CSVPointReader.h"
#include "stuff.h"

namespace Potree{

CSVPointReader::CSVPointReader(string path){

	reader = new CSVReader(path);
	aabb = reader->getAABB();

}

CSVPointReader::~CSVPointReader(){
	close();
}

void CSVPointReader::close(){
	if(reader != NULL){
		reader->close();
		delete reader;
		reader = NULL;
	}
}

long long CSVPointReader::numPoints(){
	long long points = reader->numPoints();
	return points;
}

bool CSVPointReader::readNextPoint(){

	bool hasPoints = reader->readPoint();

	if(!hasPoints){
		close();
	}

	return hasPoints;
}

Point CSVPointReader::getPoint(){
	Point const p = reader->GetPoint();
    return p;
}

AABB CSVPointReader::getAABB(){
	return aabb;
}

}
