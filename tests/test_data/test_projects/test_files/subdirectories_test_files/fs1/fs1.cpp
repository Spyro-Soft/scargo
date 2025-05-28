#include "fs1.hpp"

Fs1::Fs1(){
    this->variable=0;
}

Fs1::Fs1(unsigned int variable){
    this->variable=variable;
}

void Fs1::setVariable(unsigned int variable){
    this->variable=variable;
}

unsigned int Fs1::getVariable(){
    return this->variable;
}

Fs1::~Fs1(){

}