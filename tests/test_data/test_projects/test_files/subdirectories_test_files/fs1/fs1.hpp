#ifndef FILE_FS1_HPP
#define FILE_FS1_HPP

class Fs1{
    public:
        Fs1();
        Fs1(unsigned int variable);
        void setVariable(unsigned int variable);
        unsigned int getVariable();
        ~Fs1();
    protected:
    private:
        unsigned int variable;
};

#endif // FILE_FS1_HPP