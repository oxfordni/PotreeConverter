#ifndef LOCBPOINTREADER_H
#define LOCBPOINTREADER_H

#include <string>

#include "Point.h"
#include "PointReader.h"
#include "stuff.h"
#include "locbReader.hpp"

namespace Potree{

class LOCBReader{
private:
	Point lastReadPoint;
    int pointsRead = 0;
    oni::LocalizationResultsHeader header;
    std::vector<oni::LocalizationResult> locb_points;
    oni::FileFrameIndicesToAcquisitionData  acq_metadata;


public:

	LOCBReader(string fileName){
		loadDataFromLocbFile(fileName, header, locb_points, acq_metadata);
	}

	bool readPoint(){
		if(pointsRead == numPoints()){
			return false;
		}

		oni::LocalizationResult locb_point = locb_points[pointsRead];
		lastReadPoint = Point(locb_point.rawPosition_x,locb_point.rawPosition_y,locb_point.rawPosition_z);
		lastReadPoint.channelIndex = locb_point.channelIndex;
		lastReadPoint.frameIndex = locb_point.frameIndex;
		lastReadPoint.intensity = locb_point.intensity;
		pointsRead++;
		return true;
	}

	Point GetPoint(){
		return lastReadPoint;
	}

	long long numPoints() {
		return (long long) locb_points.size();
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

class LOCBPointReader : public PointReader{
private:
//  AABB stands for: Axis Aligned Bounding Box
	AABB aabb;
	string path;
	LOCBReader *reader;

public:

	LOCBPointReader(string path);

	~LOCBPointReader();

	bool readNextPoint();

	Point getPoint();

	AABB getAABB();

	long long numPoints();

	void close();

};

}

#endif
