#ifndef FILE_DIR_HPP
#define FILE_DIR_HPP

class Dir{
    public:
        Dir();
        Dir(unsigned int variable);
        void setVariable(unsigned int variable);
        unsigned int getVariable();
        ~Dir();
    protected:
    private:
        unsigned int variable;
};

#endif // FILE_DIR_HPP