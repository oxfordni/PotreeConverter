
#include <vector>

#include "LASPointWriter.hpp"

using std::vector;

namespace Potree{

void LASPointWriter::write(const Point &point){

	coordinates[0] = point.position.x;
	coordinates[1] = point.position.y;
	coordinates[2] = point.position.z;
	laszip_set_coordinates(writer, coordinates);
	// set points to "extended type"
	this->point->extended_point_type = 1;
	this->point->rgb[0] = (laszip_I16)(point.channelIndex);
	this->point->rgb[1] = (laszip_I16)(point.frameIndex);
	this->point->rgb[2] = point.color.z * 256;

	this->point->intensity = point.intensity;
	this->point->classification = point.classification;
	this->point->return_number = point.returnNumber;
	this->point->number_of_returns = point.numberOfReturns;
	this->point->point_source_ID = point.pointSourceID;
	
	// *((laszip_I16*)(this->point->extra_bytes + 0)) = (laszip_I16)(point.channelIndex);
	// *((laszip_I16*)(this->point->extra_bytes + 2)) = (laszip_I16)(point.frameIndex);
	laszip_set_point(writer, this->point);
	laszip_write_point(writer);

	numPoints++;
}

}