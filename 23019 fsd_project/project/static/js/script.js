$(document).ready(function () {

    // Animate cards on home page load
    $('.application-card').each(function (index) {
        $(this).css({
            'opacity': 0,
            'position': 'relative',
            'top': '20px'
        });

        $(this).delay(100 * index).animate({
            'opacity': 1,
            'top': 0
        }, 500);
    });

    // Scheme-specific Document Requirements Map
    const schemeRequirements = {
        "Ayushman Bharat (PM-JAY)": [
            { name: "aadhaar", label: "Aadhaar Card", type: "file" },
            { name: "ration_card", label: "Ration Card / Family ID", type: "file" },
            { name: "address_proof", label: "Address Proof", type: "file" },
            { name: "income_cert", label: "Income Certificate", type: "file" },
            { name: "photo", label: "Passport-size Photograph", type: "file" },
            { name: "mobile_number", label: "Mobile Number (verification)", type: "text" },
            { name: "secc_record", label: "SECC eligibility record reference", type: "file", required: false }
        ],
        "National Health Mission": [
            { name: "aadhaar", label: "Aadhaar Card", type: "file" },
            { name: "address_proof", label: "Address Proof", type: "file" },
            { name: "income_cert", label: "Income Certificate", type: "file" },
            { name: "medical_docs", label: "Medical Reports / Supporting Health Documents", type: "file" },
            { name: "photo", label: "Passport-size Photograph", type: "file" }
        ],
        "Pradhan Mantri Awas Yojana": [
            { name: "aadhaar", label: "Aadhaar Card", type: "file" },
            { name: "income_cert", label: "Income Certificate", type: "file" },
            { name: "address_proof", label: "Address Proof", type: "file" },
            { name: "bank_passbook", label: "Bank Passbook Copy", type: "file" },
            { name: "property_docs", label: "Property Ownership Documents", type: "file" },
            { name: "photo", label: "Passport-size Photograph", type: "file" },
            { name: "self_declaration", label: "Self-declaration (no permanent house affidavit)", type: "file" },
            { name: "caste_cert", label: "Caste Certificate", type: "file", required: false }
        ],
        "PM Kisan Samman Nidhi": [
            { name: "aadhaar", label: "Aadhaar Card", type: "file" },
            { name: "land_documents", label: "Land Ownership Documents", type: "file" },
            { name: "bank_passbook", label: "Bank Passbook Copy", type: "file" },
            { name: "mobile_number", label: "Mobile Number", type: "text" },
            { name: "photo", label: "Passport-size Photograph", type: "file" },
            { name: "farmer_cert", label: "Farmer registration certificate", type: "file", required: false }
        ],
        "National Social Assistance Programme": [
            { name: "aadhaar", label: "Aadhaar Card", type: "file" },
            { name: "age_proof", label: "Age Proof (Birth Certificate / Voter ID)", type: "file" },
            { name: "income_cert", label: "Income Certificate", type: "file" },
            { name: "bank_passbook", label: "Bank Account Passbook Copy", type: "file" },
            { name: "photo", label: "Passport-size Photograph", type: "file" },
            { name: "death_cert", label: "Death Certificate of spouse (Widow Pension)", type: "file", required: false },
            { name: "disability_cert", label: "Disability Certificate", type: "file", required: false }
        ],
        "National Scholarship Scheme": [
            { name: "aadhaar", label: "Aadhaar Card", type: "file" },
            { name: "bonafide_cert", label: "Bonafide Certificate (from college/school)", type: "file" },
            { name: "marks_memo", label: "Previous Marks Memo", type: "file" },
            { name: "income_cert", label: "Income Certificate", type: "file" },
            { name: "bank_passbook", label: "Bank Passbook Copy", type: "file" },
            { name: "photo", label: "Passport-size Photograph", type: "file" },
            { name: "caste_cert", label: "Caste Certificate", type: "file", required: false },
            { name: "disability_support", label: "Disability Certificate", type: "file", required: false }
        ],
        "Sukanya Samriddhi Yojana": [
            { name: "birth_cert", label: "Birth Certificate of Girl Child", type: "file" },
            { name: "parent_aadhaar", label: "Parent/Guardian Aadhaar Card", type: "file" },
            { name: "address_proof", label: "Address Proof", type: "file" },
            { name: "photo", label: "Passport-size Photograph", type: "file" },
            { name: "bank_details", label: "Bank/Post Office Account Details", type: "file" },
            { name: "guardian_proof", label: "Guardian relationship proof", type: "file", required: false }
        ],
        "MGNREGA": [
            { name: "aadhaar", label: "Aadhaar Card", type: "file" },
            { name: "residence_proof", label: "Residence Proof", type: "file" },
            { name: "bank_passbook", label: "Bank Passbook Copy", type: "file" },
            { name: "photo", label: "Passport-size Photograph", type: "file" },
            { name: "job_card_copy", label: "Job Card Application Form copy", type: "file", required: false }
        ],
        "Public Distribution System": [
            { name: "aadhaar", label: "Aadhaar Card (all family members)", type: "file" },
            { name: "address_proof", label: "Address Proof", type: "file" },
            { name: "income_cert", label: "Income Certificate", type: "file" },
            { name: "photo", label: "Passport-size Photograph", type: "file" },
            { name: "family_details", label: "Family Member Details List", type: "text" },
            { name: "gas_details", label: "Gas connection details", type: "file", required: false }
        ]
    };

    // Dynamic field manipulation based on drop down choice
    $('#scheme_name').change(function () {
        let scheme = $(this).val();
        let fields = schemeRequirements[scheme];
        let container = $('#dynamicFields');

        container.empty(); // Clear existing fields

        if (fields && fields.length > 0) {
            $('#selectedSchemeTitle').text(scheme);
            $('#dynamicFieldsContainer').removeClass('d-none').hide().fadeIn(300);

            fields.forEach(function (f) {
                let requiredAttr = f.required !== false ? 'required' : '';
                let asterisk = f.required !== false ? '<span class="text-danger">*</span>' : '<span class="text-muted small">(Optional)</span>';

                let inputHtml = `
                <div class="col-md-6 field-anim">
                    <label for="${f.name}" class="form-label fw-bold text-secondary">${f.label} ${asterisk}</label>
                    <input type="${f.type}" class="form-control" id="${f.name}" name="${f.name}" placeholder="Enter ${f.label}" ${requiredAttr}>
                </div>`;
                container.append(inputHtml);
            });

            // Minor entrance animation
            $('.field-anim').css({ opacity: 0, marginTop: '10px' }).animate({ opacity: 1, marginTop: '0px' }, 200);

        } else {
            // General "Other" scheme or none
            $('#dynamicFieldsContainer').fadeOut(200);
        }
    });

    // Form submission validation UI effect
    $('#submitBtn').click(function (e) {
        let isValid = true;

        // Loop through all required inputs in the form
        $('#trackingForm').find('input[required], select[required], textarea[required]').each(function () {
            let val = $(this).val();
            // Handle file input validation
            if ($(this).attr('type') === 'file') {
                if ($(this).get(0).files.length === 0) {
                    $(this).addClass('is-invalid');
                    isValid = false;
                } else {
                    $(this).removeClass('is-invalid').addClass('is-valid');
                }
            } else {
                // Non-file input validation
                if (!val || typeof val === 'string' && val.trim() === '') {
                    $(this).addClass('is-invalid');
                    isValid = false;
                } else {
                    $(this).removeClass('is-invalid').addClass('is-valid');
                }
            }
        });

        if (!isValid) {
            e.preventDefault(); // Stop form submission
            // Shake effect for invalid form
            $('#trackingForm').animate({ marginLeft: '-10px' }, 50)
                .animate({ marginLeft: '10px' }, 50)
                .animate({ marginLeft: '-10px' }, 50)
                .animate({ marginLeft: '0px' }, 50);
        }
    });

    // Clear validation state on input
    $(document).on('input change', 'input, select', function () {
        $(this).removeClass('is-invalid');
        if ($(this).val().trim() !== '') {
            if ($(this).attr('type') === 'email') {
                let emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (emailRegex.test($(this).val())) {
                    $(this).addClass('is-valid');
                }
            } else {
                $(this).addClass('is-valid');
            }
        } else {
            $(this).removeClass('is-valid');
        }
    });

    // Review Button Effect (UI interaction)
    $('#reviewBtn').click(function () {
        let scheme = $('#scheme_name').val();

        if (scheme) {
            $('#formConfirmation').html('<strong>Review:</strong> Submitting application for <b>' + scheme + '</b> scheme.').removeClass('d-none alert-info').addClass('alert-success');
        } else {
            $('#formConfirmation').html('Please select a scheme to review.').removeClass('d-none alert-success').addClass('alert-info');
        }

        $('#formConfirmation').hide().slideDown(300);
    });
});
