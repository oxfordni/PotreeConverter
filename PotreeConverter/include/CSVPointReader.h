#ifndef CSVPOINTREADER_H
#define CSVPOINTREADER_H

#include <string>

#include "Point.h"
#include "PointReader.h"
#include "stuff.h"
#include "csvReader.hpp"

namespace Potree{

class CSVReader{
private:
	Point lastReadPoint;
    int pointsRead = 0;
    oni::LocalizationResultsHeader header;
    std::vector<oni::LocalizationResult> csv_points;
    oni::FileFrameIndicesToAcquisitionData  acq_metadata;


public:

	CSVReader(string fileName){
		loadDataFromCsvFile(fileName, header, csv_points, acq_metadata);
	}

	bool readPoint(){
		if(pointsRead == numPoints()){
			return false;
		}

		oni::LocalizationResult csv_point = csv_points[pointsRead];
		lastReadPoint = Point(csv_point.rawPosition_x,csv_point.rawPosition_y,csv_point.rawPosition_z);
		lastReadPoint.channelIndex = csv_point.channelIndex;
		lastReadPoint.frameIndex = csv_point.frameIndex;
		lastReadPoint.intensity = csv_point.intensity;
		pointsRead++;
		return true;
	}

	Point GetPoint(){
		return lastReadPoint;
	}

	long long numPoints() {
		return (long long) csv_points.size();
	}

	void close(){

	}

//  AABB stands for: Axis Aligned Bounding Box
	AABB getAABB(){
	    AABB aabb;

		Point minp = Point(header.x_min, header.y_min, header.z_min);
		Point maxp = Point(header.x_max, header.y_max, header.z_max);
		aabb.update(minp.position);
		aabb.update(maxp.position);

		return aabb;
	}


};

class CSVPointReader : public PointReader{
private:
//  AABB stands for: Axis Aligned Bounding Box
	AABB aabb;
	string path;
	CSVReader *reader;

public:

	CSVPointReader(string path);

	~CSVPointReader();

	bool readNextPoint();

	Point getPoint();

	AABB getAABB();

	long long numPoints();

	void close();

};

}

#endif
