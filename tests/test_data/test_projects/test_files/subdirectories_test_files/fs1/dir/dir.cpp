#include "dir.hpp"

Dir::Dir(){
    this->variable=0;
}

Dir::Dir(unsigned int variable){
    this->variable=variable;
}

void Dir::setVariable(unsigned int variable){
    this->variable=variable;
}

unsigned int Dir::getVariable(){
    return this->variable;
}

Dir::~Dir(){

}